from abc import ABC
from abc import abstractmethod

from openai import OpenAI

from core.config import settings


class LLMProvider(ABC):
    """
    Base interface for all LLM providers.
    """

    @abstractmethod
    def generate(
        self,
        messages: list[dict],
        **kwargs,
    ) -> tuple[str, int]:
        """
        Generate a response.

        Returns
        -------
        (
            response_text,
            total_tokens
        )
        """
        raise NotImplementedError
    

class GroqProvider(LLMProvider):
    """
    Groq implementation.

    Uses the OpenAI-compatible SDK.
    """

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GroqProvider()

        return cls._instance

    def __init__(self):

        if hasattr(self, "client"):
            return

        self.client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )

    def generate(
        self,
        messages: list[dict],
        max_tokens: int = 1024,
        temperature: float = 0.1,
    ) -> tuple[str, int]:

        response = self.client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        answer = response.choices[0].message.content or ""

        tokens = (
            response.usage.total_tokens
            if response.usage
            else 0
        )

        return answer, tokens
    

_provider = None


def get_llm() -> LLMProvider:
    """
    Return singleton LLM provider.
    """

    global _provider

    if _provider is None:
        _provider = GroqProvider.get_instance()

    return _provider