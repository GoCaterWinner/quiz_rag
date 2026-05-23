from openai import OpenAI
from dotenv import load_dotenv
import os

"""
调用LLM
"""

load_dotenv()


def ask_llm(prompt: str) -> str:
    """
    调用LLM

    输入: prompt
    输出: AI给的完整的, 经过润色的答案
    """
    client = OpenAI(
        api_key = os.getenv("LLM_API_KEY"),
        base_url= os.getenv("LLM_BASE_URL")
    )

    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=[
        {
            "role": "system",
            "content": "你是一个考试答题助手，只根据用户给的信息回答。",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ],
    )

    return response