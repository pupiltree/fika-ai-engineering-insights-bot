import os

class LLMClient:
    def generate(self, messages):
        raise NotImplementedError

class OpenAIClient(LLMClient):
    def __init__(self):
        from langchain_openai import ChatOpenAI
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1",
            model="mistralai/mistral-7b-instruct:free"
        )
    def generate(self, messages):
        return self.llm(messages)

class LlamaClient(LLMClient):
    def __init__(self):
        from llama_cpp import Llama
        self.llama = Llama(model_path=os.getenv("LLAMA_MODEL_PATH", "llama-2-7b-chat.ggmlv3.q4_0.bin"))
    def generate(self, messages):
        prompt = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        output = self.llama(prompt)
        # Return an object with a .content attribute for compatibility
        return type("Obj", (), {"content": output["choices"][0]["text"]})()
