import re
import yaml
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class RoutingDecision:
    model_type: str
    confidence: float
    reason: str
    estimated_cost: float
    estimated_latency: float


class ModelRouter:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.complexity_threshold = self.config['routing']['complexity_threshold']
        self.max_slm_tokens = self.config['routing']['max_slm_tokens']
        self.large_input_threshold = self.config['routing'].get('large_input_threshold', 2000)
        self.gemini_preferred_threshold = self.config['routing'].get('gemini_preferred_threshold', 1000)
        self.fallback_enabled = self.config['routing']['fallback_enabled']
        
    def analyze_complexity(self, text: str) -> float:
        word_count = len(text.split())
        char_count = len(text)
        
        question_marks = text.count('?')
        complex_patterns = len(re.findall(r'\b(analyze|explain|compare|evaluate|synthesize|create|design|develop)\b', text, re.IGNORECASE))
        technical_terms = len(re.findall(r'\b(algorithm|architecture|optimization|implementation|framework|protocol)\b', text, re.IGNORECASE))
        
        complexity_score = 0.0
        complexity_score += min(word_count / 100, 0.3)
        complexity_score += min(char_count / 500, 0.2)
        complexity_score += min(question_marks * 0.1, 0.2)
        complexity_score += min(complex_patterns * 0.15, 0.2)
        complexity_score += min(technical_terms * 0.1, 0.1)
        
        return min(complexity_score, 1.0)
    
    def estimate_tokens(self, text: str) -> float:
        return len(text.split()) * 1.3
    
    def estimate_cost(self, text: str, model_type: str) -> float:
        tokens = self.estimate_tokens(text)
        if model_type == 'gemini' and 'gemini' in self.config['models']:
            cost_per_token = self.config['models']['gemini']['cost_per_token']
        else:
            cost_per_token = self.config['models'][model_type]['cost_per_token']
        return tokens * cost_per_token
    
    def estimate_latency(self, text: str, model_type: str) -> float:
        tokens = self.estimate_tokens(text)
        
        if model_type == 'gemini':
            base_latency = 1.0
            token_latency = tokens / 200
        elif model_type == 'llm':
            base_latency = 2.0
            token_latency = tokens / 100
        else:
            base_latency = 0.5
            token_latency = tokens / 500
        
        return base_latency + token_latency
    
    def route(self, text: str, priority: str = "balanced") -> RoutingDecision:
        complexity = self.analyze_complexity(text)
        word_count = len(text.split())
        estimated_tokens = self.estimate_tokens(text)
        gemini_available = 'gemini' in self.config['models']
        
        if estimated_tokens >= self.large_input_threshold and gemini_available:
            return RoutingDecision(
                model_type="gemini",
                confidence=0.95,
                reason=f"Very large input ({estimated_tokens:.0f} tokens) - routing to Gemini for speed and reliability",
                estimated_cost=self.estimate_cost(text, "gemini"),
                estimated_latency=self.estimate_latency(text, "gemini")
            )
        
        if priority == "cost":
            if complexity < 0.8 and word_count < self.max_slm_tokens:
                return RoutingDecision(
                    model_type="slm",
                    confidence=0.8,
                    reason="Low complexity task, cost-optimized",
                    estimated_cost=self.estimate_cost(text, "slm"),
                    estimated_latency=self.estimate_latency(text, "slm")
                )
        
        if priority == "speed":
            if estimated_tokens >= self.gemini_preferred_threshold and gemini_available:
                return RoutingDecision(
                    model_type="gemini",
                    confidence=0.9,
                    reason=f"Large input ({estimated_tokens:.0f} tokens) - Gemini preferred for speed",
                    estimated_cost=self.estimate_cost(text, "gemini"),
                    estimated_latency=self.estimate_latency(text, "gemini")
                )
            if complexity < 0.7:
                return RoutingDecision(
                    model_type="slm",
                    confidence=0.75,
                    reason="Simple task, speed-optimized",
                    estimated_cost=self.estimate_cost(text, "slm"),
                    estimated_latency=self.estimate_latency(text, "slm")
                )
        
        if complexity > self.complexity_threshold or word_count > self.max_slm_tokens:
            if estimated_tokens >= self.gemini_preferred_threshold and gemini_available:
                return RoutingDecision(
                    model_type="gemini",
                    confidence=0.9,
                    reason=f"High complexity ({complexity:.2f}) and large input ({estimated_tokens:.0f} tokens) - Gemini preferred",
                    estimated_cost=self.estimate_cost(text, "gemini"),
                    estimated_latency=self.estimate_latency(text, "gemini")
                )
            return RoutingDecision(
                model_type="llm",
                confidence=0.9,
                reason=f"High complexity ({complexity:.2f}) or long input",
                estimated_cost=self.estimate_cost(text, "llm"),
                estimated_latency=self.estimate_latency(text, "llm")
            )
        
        cost_weight = self.config['routing']['cost_weight']
        latency_weight = self.config['routing']['latency_weight']
        quality_weight = self.config['routing']['quality_weight']
        
        llm_cost = self.estimate_cost(text, "llm")
        slm_cost = self.estimate_cost(text, "slm")
        llm_latency = self.estimate_latency(text, "llm")
        slm_latency = self.estimate_latency(text, "slm")
        
        gemini_score = 0.0
        gemini_cost = 0.0
        gemini_latency = 0.0
        if gemini_available and estimated_tokens >= self.gemini_preferred_threshold:
            gemini_cost = self.estimate_cost(text, "gemini")
            gemini_latency = self.estimate_latency(text, "gemini")
            gemini_quality_score = min(complexity * 1.3, 1.0)
            gemini_score = (cost_weight * (1 - gemini_cost * 100)) + (latency_weight * (1 - gemini_latency / 10)) + (quality_weight * gemini_quality_score)
        
        llm_quality_score = min(complexity * 1.2, 1.0)
        slm_quality_score = max(0.5, 1.0 - complexity * 0.5)
        
        llm_score = (cost_weight * (1 - llm_cost * 100)) + (latency_weight * (1 - llm_latency / 10)) + (quality_weight * llm_quality_score)
        slm_score = (cost_weight * (1 - slm_cost * 100)) + (latency_weight * (1 - slm_latency / 10)) + (quality_weight * slm_quality_score)
        
        if gemini_available and gemini_score > 0 and gemini_score >= max(llm_score, slm_score):
            return RoutingDecision(
                model_type="gemini",
                confidence=0.85,
                reason=f"Gemini preferred for reliability and speed (score: {gemini_score:.2f}, {estimated_tokens:.0f} tokens)",
                estimated_cost=gemini_cost,
                estimated_latency=gemini_latency
            )
        
        if slm_score > llm_score and complexity < 0.7:
            return RoutingDecision(
                model_type="slm",
                confidence=0.7,
                reason=f"Balanced decision: SLM preferred (score: {slm_score:.2f})",
                estimated_cost=slm_cost,
                estimated_latency=slm_latency
            )
        
        return RoutingDecision(
            model_type="llm",
            confidence=0.85,
            reason=f"Balanced decision: LLM preferred (score: {llm_score:.2f})",
            estimated_cost=llm_cost,
            estimated_latency=llm_latency
        )

