from agno.models import openai

from app.core.config import settings


QWEN = openai.OpenAIChat(
    id=settings.qwen_model,
    api_key=settings.openai_api_key,
    base_url="https://aicredits.in/v1",
)