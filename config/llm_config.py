from pathlib import Path
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not API_KEY:
    raise ValueError("DEEPSEEK_API_KEY 未设置")


def get_llm(model: str = "deepseek-chat", temperature: float = 0.1):
    return ChatOpenAI(
        model=model,
        api_key=API_KEY,
        base_url="https://api.deepseek.com",
        temperature=temperature,
    )


deep_llm = get_llm("deepseek-chat")
quick_llm = get_llm("deepseek-chat")
