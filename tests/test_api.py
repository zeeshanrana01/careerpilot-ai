"""Unit tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from careerpilot.api.app import app

client = TestClient(app)

def test_dashboard_renders():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "CareerPilot AI" in resp.text
    assert "Ranked Opportunity Queue" in resp.text

def test_api_profile_endpoint():
    resp = client.get("/api/profile")
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Rana Zeeshan"

def test_api_matches_endpoint():
    resp = client.get("/api/matches")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_api_audit_endpoint():
    resp = client.get("/api/audit")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
