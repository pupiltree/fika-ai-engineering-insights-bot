"""Base agent class for LangChain agents."""
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate

from ..config import settings, logger
from ..data.database import db
from ..data.models import PromptLog


class BaseAgent(ABC):
    """Base class for all productivity intelligence agents."""
    
    def __init__(self, name: str, system_prompt: str = None):
        self.name = name
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.gemini_api_key,
            temperature=settings.llm_temperature,
            max_tokens=settings.max_tokens
        )
        
        # Create prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}")
        ])
        
        logger.info(f"Initialized {self.name} agent with model {settings.llm_model}")
    
    @abstractmethod
    def _get_default_system_prompt(self) -> str:
        """Return the default system prompt for this agent."""
        pass
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """Process input data and return results."""
        pass
    
    def _invoke_llm(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Invoke the LLM with logging and error handling."""
        start_time = time.time()
        
        try:
            # Format the prompt with context
            formatted_prompt = prompt
            if context:
                formatted_prompt = prompt.format(**context)
            
            # Create messages
            messages = self.prompt_template.format_messages(input=formatted_prompt)
            
            # Invoke LLM
            response = self.llm.invoke(messages)
            
            # Extract response content
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            # Calculate execution time
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log the interaction
            self._log_interaction(formatted_prompt, response_content, execution_time)
            
            logger.info(f"{self.name} LLM call completed in {execution_time}ms")
            return response_content
            
        except Exception as e:
            logger.error(f"{self.name} LLM call failed: {e}")
            raise
    
    def _log_interaction(self, prompt: str, response: str, execution_time_ms: int):
        """Log the prompt/response interaction to database."""
        log_entry = PromptLog(
            agent_name=self.name,
            prompt=prompt,
            response=response,
            timestamp=datetime.now(),
            execution_time_ms=execution_time_ms,
            token_count=self._estimate_token_count(prompt + response)
        )
        
        success = db.log_prompt(log_entry)
        if not success:
            logger.warning(f"Failed to log interaction for {self.name}")
    
    def _estimate_token_count(self, text: str) -> int:
        """Rough token count estimation (4 chars ≈ 1 token for English)."""
        return len(text) // 4
    
    def _format_data_for_prompt(self, data: List[Any], max_items: int = 50) -> str:
        """Format data objects for inclusion in prompts."""
        if not data:
            return "No data available."
        
        # Limit data to prevent context overflow
        limited_data = data[:max_items]
        
        formatted_items = []
        for item in limited_data:
            if hasattr(item, 'dict'):
                # Pydantic model
                formatted_items.append(str(item.dict()))
            else:
                formatted_items.append(str(item))
        
        result = "\n".join(formatted_items)
        
        if len(data) > max_items:
            result += f"\n... and {len(data) - max_items} more items"
        
        return result
    
    def _retry_on_failure(self, func, max_retries: int = None, *args, **kwargs):
        """Retry a function call on failure with exponential backoff."""
        max_retries = max_retries or settings.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"{self.name} failed after {max_retries} retries: {e}")
                    raise
                
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"{self.name} attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": self.name,
            "model": settings.llm_model,
            "temperature": settings.llm_temperature,
            "max_tokens": settings.max_tokens,
            "system_prompt_length": len(self.system_prompt)
        }


class AgentError(Exception):
    """Custom exception for agent-related errors."""
    
    def __init__(self, agent_name: str, message: str, original_error: Exception = None):
        self.agent_name = agent_name
        self.original_error = original_error
        super().__init__(f"[{agent_name}] {message}")


class AgentTimeoutError(AgentError):
    """Exception raised when agent operations timeout."""
    pass


class AgentValidationError(AgentError):
    """Exception raised when agent input/output validation fails."""
    pass