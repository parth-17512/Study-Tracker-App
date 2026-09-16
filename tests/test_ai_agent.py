import pytest
from app.ai.agent import StudyCoachAgent
from app.ai.providers.mock import MockLLMProvider

# Since AnalyticsService depends on the DB, we want to mock it or just verify the router handles it.
# We'll just verify the router structure works and handles known/unknown tools.

@pytest.fixture
def agent():
    return StudyCoachAgent(provider=MockLLMProvider())

def test_get_available_tools(agent):
    tools = agent.get_available_tools()
    assert isinstance(tools, list)
    assert len(tools) > 0
    
    names = [t["name"] for t in tools]
    assert "get_today_stats" in names
    assert "get_streak" in names
    
def test_execute_unknown_tool(agent):
    result = agent.execute_tool("launch_missiles")
    assert "error" in result
    assert "Unknown tool" in result["error"]
    
def test_execute_stubbed_tool(agent):
    result = agent.execute_tool("get_goal_progress")
    assert "error" in result
    assert "not implemented" in result["error"]

# We can't strictly test execute_tool("get_today_stats") without a test DB or mocking, 
# but the methods have been mapped correctly.
