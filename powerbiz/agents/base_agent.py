"""
Base agent module for PowerBiz
"""

import os
import logging
from typing import Dict, Any, List
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler

from powerbiz.database.db import get_session
from powerbiz.database.models import PromptLog

logger = logging.getLogger(__name__)

class PromptLoggerCallback(BaseCallbackHandler):
    """Callback handler to log prompts and responses."""
    
    def __init__(self, agent_name: str, prompt_type: str):
        """Initialize callback.
        
        Args:
            agent_name: Name of the agent (data_harvester, diff_analyst, insight_narrator)
            prompt_type: Type of prompt (e.g., 'analyze_commit', 'generate_report')
        """
        self.agent_name = agent_name
        self.prompt_type = prompt_type
        self.prompt_content = ""
        self.response_content = ""
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """Log prompt content."""
        self.prompt_content = "\n".join(prompts)
    
    def on_llm_end(self, response, **kwargs):
        """Log response content and save to database."""
        self.response_content = str(response.generations[0][0].text)
        
        # Save to database
        session = get_session()
        try:
            log_entry = PromptLog(
                agent_name=self.agent_name,
                prompt_type=self.prompt_type,
                prompt_content=self.prompt_content,
                response_content=self.response_content
            )
            session.add(log_entry)
            session.commit()
        except Exception as e:
            logger.error(f"Failed to log prompt: {e}")
        finally:
            session.close()


class BaseAgent:
    """Base agent class for PowerBiz agents."""
    
    def __init__(self, agent_name: str, temperature: float = 0.2):
        """Initialize the base agent.
        
        Args:
            agent_name: Name of the agent
            temperature: Temperature for the LLM
        """
        self.agent_name = agent_name
        self.temperature = temperature
        
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            logger.warning("OPENAI_API_KEY not set. LLM calls will fail.")
        
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=self.temperature,
            api_key=openai_api_key
        )
    
    def create_logger_callback(self, prompt_type: str) -> PromptLoggerCallback:
        """Create a callback to log prompts and responses.
        
        Args:
            prompt_type: Type of prompt
            
        Returns:
            Callback handler
        """
        return PromptLoggerCallback(self.agent_name, prompt_type)
