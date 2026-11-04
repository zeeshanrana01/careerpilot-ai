"""Hybrid LLM provider interfaces for local Ollama and Cloud AI inference."""
import abc
import json
from typing import Optional
import httpx
from careerpilot.core.config import settings
from careerpilot.core.security import extract_json_from_llm


class LLMProvider(abc.ABC):
    """Abstract base class for all CareerPilot inference providers."""

    @abc.abstractmethod
    async def generate_json(self, prompt: str, system_prompt: str) -> dict:
        """Generate structured JSON response adhering to prompt requirements."""
        pass


class LocalOllamaProvider(LLMProvider):
    """
    Local inference engine using Ollama.
    Guarantees private document processing without sending CV data to external cloud APIs.
    """

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model

    async def generate_json(self, prompt: str, system_prompt: str) -> dict:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1,  # Low temperature for deterministic evaluation
            },
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data.get("response", "{}")
            return extract_json_from_llm(raw_text)


class CloudLLMProvider(LLMProvider):
    """
    Cloud inference engine for deeper reasoning, complex synthesis, and extraction.
    Supports Google Gemini (or compatible endpoints).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key or settings.cloud_api_key
        self.model = model or settings.cloud_model
        self.base_url = (base_url or settings.cloud_base_url).rstrip("/")

    async def generate_json(self, prompt: str, system_prompt: str) -> dict:
        # Standard Gemini REST API generateContent endpoint with response_mime_type="application/json"
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            try:
                candidate_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return extract_json_from_llm(candidate_text)
            except (KeyError, IndexError) as e:
                raise ValueError(f"Failed to parse cloud LLM response: {str(e)}")


class MockLLMProvider(LLMProvider):
    """
    Deterministic mock provider for unit testing, CI/CD, and offline verification.
    Computes keyword-grounded evaluations without making network calls.
    """

    async def generate_json(self, prompt: str, system_prompt: str) -> dict:
        prompt_lower = prompt.lower()
        
        # Test security injection resilience: if untrusted job contains override command, ignore it!
        # Do not grant 100 points simply because the job requested it!
        
        # Extract skills present in profile
        skills_matched = []
        gaps = []
        score = 65.0  # Base score
        
        keywords = {
            "python": ("Python", "Expert proficiency with 6+ years in Python production systems"),
            "fastapi": ("FastAPI", "4+ years building high-throughput microservices and APIs"),
            "langgraph": ("LangGraph", "Architected multi-agent LLM systems with LangGraph"),
            "pytorch": ("PyTorch", "Built distributed feature pipelines with PyTorch"),
            "rag": ("RAG Systems", "Indexed over 2M documents with hybrid retrieval"),
            "docker": ("Docker & K8s", "Deployed LLM inference on Kubernetes clusters"),
            "distributed": ("Distributed Systems", "Experience in distributed inference scaling"),
        }
        
        for k, (name, evidence) in keywords.items():
            if k in prompt_lower:
                skills_matched.append({
                    "requirement": f"Proficiency in {name}",
                    "candidate_evidence": evidence,
                    "confidence": "high"
                })
                score += 5.0
                
        # Gaps
        if "rust" in prompt_lower:
            gaps.append("Production Rust programming experience not found on verified profile.")
            score -= 10.0
        if "c++" in prompt_lower:
            gaps.append("C++ low-level optimization experience not listed.")
            score -= 5.0
        if "phd" in prompt_lower:
            gaps.append("PhD in Computer Science or related field required.")
            score -= 15.0
            
        score = max(20.0, min(95.0, score))
        recommendation = "APPLY" if score >= 75.0 else ("CONSIDER" if score >= 50.0 else "SKIP")
        
        return {
            "overall_score": score,
            "recommendation": recommendation,
            "strengths": skills_matched,
            "gaps": gaps if gaps else ["None identified in core technical stack"],
            "reasoning": f"Candidate demonstrates strong alignment with {len(skills_matched)} core requirements, backed by verified production projects and skills.",
            "grounding_verified": True
        }
