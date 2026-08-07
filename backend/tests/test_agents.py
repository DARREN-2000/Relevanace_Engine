import pytest
from app.agents.copy_agent import CopyAgent
from app.agents.segment_agent import SegmentAgent


def test_copy_agent_fallback(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    agent = CopyAgent()
    assert agent.client is None

    with pytest.raises(ValueError, match="OpenAI API key missing or invalid"):
        agent.generate_copy({"product": "TestPlatform"}, "friendly")


def test_segment_agent_fallback(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    agent = SegmentAgent()
    assert agent.client is None

    with pytest.raises(ValueError, match="OpenAI API key missing or invalid"):
        agent.generate_audience("activation")
