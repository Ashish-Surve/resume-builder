"""
PerplexityClient: LangChain wrapper around Perplexity Chat models.
Requires:
  - uv add langchain-perplexity
  - PPLX_API_KEY in environment
"""

from typing import List, Dict, Any
from langchain_perplexity import ChatPerplexity
from langchain_core.messages import HumanMessage, SystemMessage


class PerplexityClient:
    def __init__(self, api_key: str | None = None, model: str = "llama-3.1-sonar-small-128k-online", temperature: float = 0.7):
        # If api_key is None, ChatPerplexity will read from PPLX_API_KEY env var
        self.chat = ChatPerplexity(model=model, temperature=temperature, api_key=api_key,timeout=300)

    def invoke(self, system: str, user: str) -> str:
        msgs = [SystemMessage(content=system), HumanMessage(content=user)]
        resp = self.chat.invoke(msgs)
        return getattr(resp, "content", str(resp))

    def analyze_resume_job_match(self, resume_text: str, job_text: str) -> Dict[str, Any]:
        prompt = f"""As an ATS analyst, analyze this resume vs job.
Job:
{job_text}

Resume:
{resume_text}

Return a concise analysis with a 0-100 score, missing keywords, and 3 recommendations."""
        content = self.invoke("You are an expert ATS analyst.", prompt)
        return {"raw_response": content}

    def optimize_section(self, section_text: str, keywords: List[str], section_type: str) -> str:
        prompt = f"""Optimize this {section_type} section to naturally include: {', '.join(keywords)}.
Keep truthful, use action verbs and quantifiable impact:
{section_text}"""
        return self.invoke("You are an expert resume writer.", prompt)
