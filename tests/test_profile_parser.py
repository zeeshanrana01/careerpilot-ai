"""Tests for resume and CV parser."""
import json
import pytest
from careerpilot.profile.parser import parse_resume_text, parse_resume_file
from careerpilot.domain.models import CareerProfile

SAMPLE_RESUME_TEXT = """
Rana Zeeshan
rana.zeeshan@example.com | +92 300 1234567 | Lahore, Pakistan

SUMMARY
Applied AI Engineer with extensive experience building autonomous agents, RAG systems, and production LLM applications using Python, FastAPI, and Docker.

TECHNICAL SKILLS
Languages: Python, TypeScript, SQL, Bash
Frameworks & AI: FastAPI, LangChain, LangGraph, PyTorch, Ollama, Docker, Kubernetes, Next.js

WORK EXPERIENCE
Senior AI Engineer - Alpha AI Systems (2022 - Present)
- Designed and deployed enterprise multi-agent workflows with LangGraph.
- Built low-latency FastAPI microservices serving LLM inference.
- Implemented automated prompt injection defenses and RAG pipelines.

PROJECTS
CareerPilot AI - Lead Architect
- Hybrid local/cloud AI career assistant with explainable match scoring.
- Built zero-hallucination claim verification engine.
"""

def test_parse_resume_text_basic():
    profile = parse_resume_text(SAMPLE_RESUME_TEXT)
    assert isinstance(profile, CareerProfile)
    assert profile.full_name == "Rana Zeeshan"
    assert profile.email == "rana.zeeshan@example.com"
    assert any(s.name == "Python" for s in profile.skills)
    assert any(s.name == "FastAPI" for s in profile.skills)
    assert len(profile.experience) >= 1
    assert len(profile.projects) >= 1

def test_parse_resume_file_json():
    json_bytes = json.dumps({
        "full_name": "Rana Zeeshan",
        "email": "rana.zeeshan@example.com",
        "headline": "Lead AI Engineer",
        "summary": "Specialist in agentic AI and LLM evaluation.",
        "skills": [{"name": "Python", "category": "technical", "years_experience": 5.0, "proficiency": "expert"}],
        "experience": [],
        "projects": [],
        "certifications": [],
    }).encode("utf-8")

    profile = parse_resume_file("profile.json", json_bytes)
    assert profile.full_name == "Rana Zeeshan"
    assert profile.headline == "Lead AI Engineer"
    assert len(profile.skills) == 1
    assert profile.skills[0].name == "Python"

def test_parse_empty_resume_raises_error():
    with pytest.raises(ValueError):
        parse_resume_text("   \n\n  ")
