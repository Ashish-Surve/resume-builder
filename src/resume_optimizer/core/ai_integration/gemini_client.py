from typing import List, Optional
import os
from pydantic import SecretStr
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

class GeminiClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
    ):
        # Use env if not provided; match expected SecretStr | None
        key = api_key or os.getenv("GOOGLE_API_KEY")
        secret = SecretStr(key) if key is not None else None
        self.chat = ChatGoogleGenerativeAI(model=model, temperature=temperature, api_key=secret)

    def invoke(self, system: str, user: str) -> str:
        msgs = [SystemMessage(content=system), HumanMessage(content=user)]
        resp = self.chat.invoke(msgs)
        return getattr(resp, "content", str(resp))

    def optimize_section(self, section_text: str, keywords: List[str], section_type: str) -> str:
        prompt = f"""Optimize this {section_type} section to include: {', '.join(keywords)}.
Keep ATS-friendly, concise, and truthful:
{section_text}"""
        return self.invoke("You are an expert resume writer.", prompt)
