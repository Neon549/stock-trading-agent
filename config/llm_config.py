# config/llm_config.py
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

# 先尝试读 .env，读不到就用系统环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_llm(model: str = "qwen-plus", temperature: float = 0.1):
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY 未设置")
    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature=temperature,
    )

deep_llm = get_llm("qwen-plus")
quick_llm = get_llm("qwen-turbo")