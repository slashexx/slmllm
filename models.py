import requests
import os
from typing import Optional, Dict, Any

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class LLMProvider:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get('provider', 'ollama')
        self.model = config.get('model', 'llama3')
        self.endpoint = config.get('endpoint')
        
        if self.provider == 'gemini':
            if not GEMINI_AVAILABLE:
                raise Exception("google-genai package not installed. Install with: pip install google-genai")
            api_key = config.get('api_key') or os.getenv('GEMINI_API_KEY', '')
            if api_key:
                os.environ['GEMINI_API_KEY'] = api_key
            self.client = genai.Client()
    
    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        if self.provider == 'ollama':
            try:
                response = requests.post(
                    self.endpoint,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens or self.config.get('max_tokens', 4096)
                        }
                    },
                    timeout=120
                )
                response.raise_for_status()
                result = response.json()
                if 'message' in result and 'content' in result['message']:
                    return result['message']['content']
                return result.get('message', {}).get('content', '')
            except Exception as e:
                raise Exception(f"Ollama API error: {str(e)}")
        
        elif self.provider == 'gemini':
            try:
                model_name = self.config.get('model', 'gemini-2.5-flash')
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return response.text
            except Exception as e:
                raise Exception(f"Gemini API error: {str(e)}")
        
        else:
            raise Exception(f"Unsupported provider: {self.provider}")


class SLMProvider:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get('provider', 'ollama')
        self.model = config.get('model', 'llama3.2')
        self.endpoint = config.get('endpoint')
        
        if self.provider == 'gemini':
            if not GEMINI_AVAILABLE:
                raise Exception("google-genai package not installed. Install with: pip install google-genai")
            api_key = config.get('api_key') or os.getenv('GEMINI_API_KEY', '')
            if api_key:
                os.environ['GEMINI_API_KEY'] = api_key
            self.client = genai.Client()
    
    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        if self.provider == 'ollama':
            try:
                response = requests.post(
                    self.endpoint,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens or self.config.get('max_tokens', 2048)
                        }
                    },
                    timeout=60
                )
                response.raise_for_status()
                result = response.json()
                if 'message' in result and 'content' in result['message']:
                    return result['message']['content']
                return result.get('message', {}).get('content', '')
            except Exception as e:
                raise Exception(f"Ollama API error: {str(e)}")
        
        elif self.provider == 'gemini':
            try:
                model_name = self.config.get('model', 'gemini-2.5-flash')
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return response.text
            except Exception as e:
                raise Exception(f"Gemini API error: {str(e)}")
        
        else:
            raise Exception(f"Unsupported provider: {self.provider}")

