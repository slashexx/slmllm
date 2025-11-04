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
            if decision.model_type == "gemini":
                if not self.gemini_fallback:
                    raise Exception("Gemini routing requested but Gemini not configured")
                response = self.gemini_fallback.generate(prompt)
                return {
                    "response": response,
                    "model_used": "gemini",
                    "decision": decision,
                    "fallback_used": False
                }
            elif decision.model_type == "llm":
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
                        if self.gemini_fallback:
                            response = self.gemini_fallback.generate(prompt)
                            return {
                                "response": response,
                                "model_used": "gemini",
                                "decision": decision,
                                "fallback_used": True,
                                "fallback_reason": "SLM response quality insufficient, using Gemini"
                            }
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
                    if self.gemini_fallback:
                        response = self.gemini_fallback.generate(prompt)
                        return {
                            "response": response,
                            "model_used": "gemini",
                            "decision": decision,
                            "fallback_used": True,
                            "fallback_reason": f"SLM error: {str(e)}, using Gemini"
                        }
                    response = self._try_generate_with_fallback(self.llm, prompt, "LLM")
                    return {
                        "response": response,
                        "model_used": "llm",
                        "decision": decision,
                        "fallback_used": True,
                        "fallback_reason": f"SLM error: {str(e)}"
                    }
                except Exception as llm_error:
                    raise Exception(f"All models failed. SLM: {str(e)}, LLM/Gemini: {str(llm_error)}")
            elif decision.model_type == "llm" and self.gemini_fallback:
                try:
                    response = self.gemini_fallback.generate(prompt)
                    return {
                        "response": response,
                        "model_used": "gemini",
                        "decision": decision,
                        "fallback_used": True,
                        "fallback_reason": f"LLM error: {str(e)}, using Gemini"
                    }
                except Exception as gemini_error:
                    raise Exception(f"Both LLM and Gemini failed. LLM: {str(e)}, Gemini: {str(gemini_error)}")
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
    
    def distill_and_process(self, prompt: str) -> Dict[str, Any]:
        distillation_prompt = f"""You are a prompt optimizer. Your task is to refine and narrow down the following user prompt to make it more focused, clear, and effective for a large language model.

Original prompt: {prompt}

Provide a refined, concise version of this prompt that:
1. Maintains the core intent
2. Removes unnecessary details
3. Clarifies any ambiguities
4. Focuses on the key question or request

Return only the refined prompt, nothing else."""
        
        try:
            refined_prompt = self._try_generate_with_fallback(self.slm, distillation_prompt, "SLM")
            
            if not refined_prompt or len(refined_prompt.strip()) < 10:
                refined_prompt = prompt
            
            refined_prompt = refined_prompt.strip()
            
            if self.gemini_fallback:
                final_response = self.gemini_fallback.generate(refined_prompt)
                model_used = "gemini"
            else:
                final_response = self._try_generate_with_fallback(self.llm, refined_prompt, "LLM")
                model_used = "llm"
            
            return {
                "response": final_response,
                "model_used": model_used,
                "refined_prompt": refined_prompt,
                "original_prompt": prompt,
                "distillation_used": True
            }
        except Exception as e:
            if self.gemini_fallback:
                try:
                    final_response = self.gemini_fallback.generate(prompt)
                    return {
                        "response": final_response,
                        "model_used": "gemini",
                        "refined_prompt": prompt,
                        "original_prompt": prompt,
                        "distillation_used": False,
                        "distillation_error": str(e)
                    }
                except Exception as gemini_error:
                    raise Exception(f"Distillation and fallback failed. Distillation: {str(e)}, Gemini: {str(gemini_error)}")
            raise Exception(f"Distillation failed: {str(e)}")
    
    def _check_response_quality(self, response: str, prompt: str) -> bool:
        if not response or len(response) < 10:
            return False
        
        if len(response) < len(prompt) * 0.1:
            return False
        
        error_indicators = ["error", "cannot", "unable", "sorry", "i don't know"]
        response_lower = response.lower()
        error_count = sum(1 for indicator in error_indicators if indicator in response_lower)
        
        return error_count < 2

