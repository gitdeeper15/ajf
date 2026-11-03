"""Tool-Using Agent (calls World Bank API for multiple indicators)."""
from ajf.agents.base_agent import BaseAgent
from typing import Dict, Any
import requests

class ToolAgent(BaseAgent):
    """Agent that uses World Bank API to fetch indicators."""
    
    def __init__(self):
        self.base_url = "https://api.worldbank.org/v2/country/MA/indicator"
        self.indicators = {
            "population": "SP.POP.TOTL",
            "gdp": "NY.GDP.MKTP.CD",
            "water": "ER.H2O.FWTL.K3",
        }
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        description = task.get("description", "").lower()
        
        # Determine which indicator to fetch
        indicator = None
        if "population" in description:
            indicator = self.indicators["population"]
        elif "gdp" in description:
            indicator = self.indicators["gdp"]
        elif "water" in description or "freshwater" in description:
            indicator = self.indicators["water"]
        else:
            return {
                "agent_id": "AGENT-C-TOOL",
                "task_id": task.get("task_id", "UNKNOWN"),
                "response": "[Tool Agent] No matching indicator found.",
                "tool_calls": [],
                "retrieved_evidence": [],
                "execution_status": "no_indicator",
            }
        
        try:
            response = requests.get(
                f"{self.base_url}/{indicator}?format=json&date=2022",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                value = data[1][0]["value"] if data[1] else "N/A"
                result = f"{indicator} (2022): {value}"
            else:
                result = f"API call failed: {response.status_code}"
        except Exception as e:
            result = f"Tool error: {e}"
        
        return {
            "agent_id": "AGENT-C-TOOL",
            "task_id": task.get("task_id", "UNKNOWN"),
            "response": f"[Tool Agent] {result}",
            "tool_calls": [f"world_bank_api:{indicator}"],
            "retrieved_evidence": [result],
            "execution_status": "success",
        }
