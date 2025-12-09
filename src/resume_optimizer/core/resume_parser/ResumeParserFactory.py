from .GeminiParser import GeminiResumeParser
from .parser import BaseResumeParser
from .parser import SpacyResumeParser

from typing import Optional
from ..ai_integration.gemini_client import GeminiClient

class ResumeParserFactory:
    """Factory class for creating resume parsers."""

    @staticmethod
    def create_parser(parser_type: str = "gemini", gemini_client: Optional[GeminiClient] = None) -> BaseResumeParser:
        """Create a resume parser instance."""
        if parser_type == "spacy":
            return SpacyResumeParser(gemini_client=gemini_client)
        elif parser_type == "gemini":
            from .GeminiParser import GeminiResumeParser
            return GeminiResumeParser(gemini_client=gemini_client)
        else:
            raise ValueError(f"Unknown parser type: {parser_type}")