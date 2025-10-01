"""
GeminiClient: LangChain wrapper around Google Gemini chat models.
Requires:
  - uv add langchain-google-genai
  - GOOGLE_API_KEY in environment
"""

from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage


class GeminiClient:
    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-flash", temperature: float = 0.7):
        # If api_key is None, ChatGoogleGenerativeAI will read from GOOGLE_API_KEY env var
        self.chat = ChatGoogleGenerativeAI(model=model, temperature=temperature, api_key=api_key)

    def invoke(self, system: str, user: str) -> str:
        msgs = [SystemMessage(content=system), HumanMessage(content=user)]
        resp = self.chat.invoke(msgs)
        return getattr(resp, "content", str(resp))

    def optimize_section(self, section_text: str, keywords: List[str], section_type: str) -> str:
        prompt = f"""Optimize this {section_type} section to include: {', '.join(keywords)}.
Keep ATS-friendly, concise, and truthful:
{section_text}"""
        return self.invoke("You are an expert resume writer.", prompt)
