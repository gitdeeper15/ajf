"""Zero-Shot Judge using Groq API via requests."""
import os
import json
import requests
from ajf.judges.base_judge import BaseJudge
from typing import Dict, Any

class ZeroShotJudge(BaseJudge):
    """Judge that evaluates without mandatory evidence verification."""
    
    def __init__(self, model_name: str = "openai/gpt-oss-120b"):
        self.model_name = model_name
        self.api_key = os.environ.get("GROQ_API_KEY", "")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def evaluate(self, task: Dict[str, Any], agent_output: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""You are an impartial judge. Evaluate the following agent response.

Task: {task.get('description', '')}
Expected Outcome: {task.get('expected_outcome', '')}
Agent Response: {agent_output.get('response', '')}

Score the response from 0 to 100 based on accuracy and completeness.
Estimate your confidence (0.0 to 1.0) based on:
  - Whether the response clearly addresses the task.
  - Whether the response contains verifiable claims.
  - Whether the expected outcome is unambiguous.

Return ONLY a JSON object with: {{"score": <int>, "confidence": <float>, "reasoning": "<string>"}}
"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                return {
                    "judge_id": "JUDGE-ZERO-SHOT",
                    "task_id": task.get("task_id", "UNKNOWN"),
                    "agent_id": agent_output.get("agent_id", "UNKNOWN"),
                    "score": parsed.get("score", 50),
                    "confidence": parsed.get("confidence", 0.5),
                    "evidence_validity": "not_checked",
                    "evaluation_status": "success",
                }
            else:
                return self._fallback(task, agent_output, f"api_error: {response.status_code}")
        except Exception as e:
            return self._fallback(task, agent_output, f"error: {e}")
    
    def _fallback(self, task, agent_output, status):
        return {
            "judge_id": "JUDGE-ZERO-SHOT",
            "task_id": task.get("task_id", "UNKNOWN"),
            "agent_id": agent_output.get("agent_id", "UNKNOWN"),
            "score": 50,
            "confidence": 0.0,
            "evidence_validity": "not_checked",
            "evaluation_status": status,
        }
