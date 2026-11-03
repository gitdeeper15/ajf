"""Direct Answer Agent (no external tools)."""
from ajf.agents.base_agent import BaseAgent
from typing import Dict, Any

class DirectAgent(BaseAgent):
    """Agent that answers using only model knowledge."""
    
    def __init__(self, model_name: str = "mock-model"):
        self.model_name = model_name
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Mock execution: returns a dummy answer
        return {
            "agent_id": "AGENT-A-DIRECT",
            "task_id": task.get("task_id", "UNKNOWN"),
            "response": f"[Mock Answer] The answer to '{task.get('description', '')}' is 42.",
            "tool_calls": [],
            "execution_status": "success",
        }
