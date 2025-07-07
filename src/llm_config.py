from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import LlamaCpp

def get_llm(driver: str = "openai"):
    if driver == "llama":
        return LlamaCpp(model_path="/models/llama-3.bin")
    return ChatOpenAI(temperature=0.7)
