import os
from openai import OpenAI

_client = None


def get_client() -> OpenAI:
    """获取大模型客户端单例"""
    global _client
    if _client is None:
        api_key = os.getenv("DASHSCOPE_API_KEY")
        _client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
    return _client


def chat_stream(messages: list, model: str = "qwen-plus"):
    """流式调用大模型，返回迭代器"""
    client = get_client()
    return client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )


def chat_completion(messages: list, model: str = "qwen-plus") -> str:
    """非流式调用大模型，返回完整文本"""
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=False
    )
    return response.choices[0].message.content
