import yaml
from typing import Dict, Any, Optional
from router import ModelRouter, RoutingDecision
from models import LLMProvider, SLMProvider


class HybridOrchestrator:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.router = ModelRouter(config_path)
        self.llm = LLMProvider(self.config['models']['llm'])
        self.slm = SLMProvider(self.config['models']['slm'])
        self.fallback_enabled = self.config['routing']['fallback_enabled']
        
        if 'gemini' in self.config['models']:
            self.gemini_fallback = LLMProvider(self.config['models']['gemini'])
        else:
            self.gemini_fallback = None
    
    def process(self, prompt: str, priority: str = "balanced", use_llm_fallback: bool = True) -> Dict[str, Any]:
        decision = self.router.route(prompt, priority)
        
        try:
            if decision.model_type == "llm":
                response = self._try_generate_with_fallback(self.llm, prompt, "LLM")
                return {
                    "response": response,
                    "model_used": "llm",
                    "decision": decision,
                    "fallback_used": False
                }
            else:
                response = self._try_generate_with_fallback(self.slm, prompt, "SLM")
                
                if use_llm_fallback and self.fallback_enabled:
                    quality_check = self._check_response_quality(response, prompt)
                    if not quality_check:
                        response = self._try_generate_with_fallback(self.llm, prompt, "LLM")
                        return {
                            "response": response,
                            "model_used": "llm",
                            "decision": decision,
                            "fallback_used": True,
                            "fallback_reason": "SLM response quality insufficient"
                        }
                
                return {
                    "response": response,
                    "model_used": "slm",
                    "decision": decision,
                    "fallback_used": False
                }
        
        except Exception as e:
            if decision.model_type == "slm" and use_llm_fallback and self.fallback_enabled:
                try:
                    response = self._try_generate_with_fallback(self.llm, prompt, "LLM")
                    return {
                        "response": response,
                        "model_used": "llm",
                        "decision": decision,
                        "fallback_used": True,
                        "fallback_reason": f"SLM error: {str(e)}"
                    }
                except Exception as llm_error:
                    raise Exception(f"Both models failed. SLM: {str(e)}, LLM: {str(llm_error)}")
            else:
                raise e
    
    def _try_generate_with_fallback(self, provider, prompt: str, model_name: str) -> str:
        try:
            return provider.generate(prompt)
        except Exception as e:
            error_str = str(e).lower()
            if ("ollama" in error_str and "connection" in error_str) or ("connection error" in error_str):
                if self.gemini_fallback:
                    return self.gemini_fallback.generate(prompt)
                else:
                    raise Exception(f"{model_name} failed (Ollama not available) and Gemini fallback not configured")
            raise e
    
    def _check_response_quality(self, response: str, prompt: str) -> bool:
        if not response or len(response) < 10:
            return False
        
        if len(response) < len(prompt) * 0.1:
            return False
        
        error_indicators = ["error", "cannot", "unable", "sorry", "i don't know"]
        response_lower = response.lower()
        error_count = sum(1 for indicator in error_indicators if indicator in response_lower)
        
        return error_count < 2

