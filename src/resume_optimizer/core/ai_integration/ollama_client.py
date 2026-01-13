# src/resume_optimizer/core/ai_integration/ollama_client.py
"""
Ollama client for local LLM integration.
Uses Llama 3.1 or other models running locally via Ollama.
"""

import logging
import requests
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Client for interacting with Ollama API for local LLM inference.
    Optimized for Llama 3.1 8B model for resume parsing.
    """

    DEFAULT_MODEL = "llama3.1:8b"
    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 120
    ):
        """
        Initialize Ollama client.

        Args:
            model: Model name (default: llama3.1:8b)
            base_url: Ollama server URL (default: http://localhost:11434)
            timeout: Request timeout in seconds
        """
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

    def is_available(self) -> bool:
        """Check if Ollama server is running and model is available."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name', '') for m in models]
                # Check if our model or a variant is available
                for name in model_names:
                    if self.model.split(':')[0] in name:
                        return True
                # If specific model not found, check if any llama model exists
                return any('llama' in name.lower() for name in model_names)
            return False
        except Exception as e:
            self.logger.debug(f"Ollama not available: {e}")
            return False

    def list_models(self) -> list:
        """List available models on Ollama server."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [m.get('name', '') for m in models]
            return []
        except Exception:
            return []

    def invoke(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> str:
        """
        Send a prompt to the Ollama model and get a response.

        Args:
            system_prompt: System message to set context
            user_prompt: User message/query
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum tokens in response

        Returns:
            Model response as string
        """
        try:
            # Use the generate endpoint with full prompt
            full_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }

            self.logger.info(f"Sending request to Ollama ({self.model})...")

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                self.logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                raise Exception(f"Ollama API error: {response.status_code}")

        except requests.exceptions.Timeout:
            self.logger.error("Ollama request timed out")
            raise Exception("Ollama request timed out. The model may be loading or the prompt is too long.")
        except requests.exceptions.ConnectionError:
            self.logger.error("Could not connect to Ollama server")
            raise Exception("Could not connect to Ollama. Make sure Ollama is running (ollama serve).")
        except Exception as e:
            self.logger.error(f"Ollama invocation failed: {e}")
            raise

    def invoke_chat(
        self,
        messages: list,
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> str:
        """
        Send a chat-style prompt using the chat endpoint.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Model response as string
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }

            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('message', {}).get('content', '').strip()
            else:
                self.logger.error(f"Ollama chat API error: {response.status_code}")
                raise Exception(f"Ollama API error: {response.status_code}")

        except Exception as e:
            self.logger.error(f"Ollama chat invocation failed: {e}")
            raise

    def invoke_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """
        Send a prompt and parse the response as JSON.

        Args:
            system_prompt: System message
            user_prompt: User message
            temperature: Sampling temperature

        Returns:
            Parsed JSON response as dict
        """
        response = self.invoke(system_prompt, user_prompt, temperature)

        # Try to extract JSON from response
        try:
            # First try direct parsing
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            import re

            # Look for JSON object
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            # Look for JSON array
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            self.logger.warning("Could not parse JSON from Ollama response")
            return {}


def check_ollama_available(base_url: str = "http://localhost:11434") -> bool:
    """
    Quick check if Ollama is available.

    Args:
        base_url: Ollama server URL

    Returns:
        True if Ollama is running
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=3)
        return response.status_code == 200
    except Exception:
        return False


def get_available_models(base_url: str = "http://localhost:11434") -> list:
    """
    Get list of available models from Ollama.

    Args:
        base_url: Ollama server URL

    Returns:
        List of model names
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [m.get('name', '') for m in models]
        return []
    except Exception:
        return []
