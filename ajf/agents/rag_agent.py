"""RAG-Based Agent (retrieves from local knowledge base)."""
from ajf.agents.base_agent import BaseAgent
from typing import Dict, Any
import json
import os

class RAGAgent(BaseAgent):
    """Agent that retrieves relevant information from a knowledge base before responding."""
    
    def __init__(self, knowledge_base_path: str = "DATA/knowledge_base.json"):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict:
        if os.path.exists(self.knowledge_base_path):
            with open(self.knowledge_base_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Mock retrieval: search for relevant keywords in the task description
        query = task.get("description", "").lower()
        relevant_docs = []
        for key, value in self.knowledge_base.items():
            if any(word in query for word in key.lower().split()):
                relevant_docs.append(f"{key}: {value}")
        
        response = f"[RAG Agent] Retrieved {len(relevant_docs)} relevant documents. "
        if relevant_docs:
            response += f"Found: {relevant_docs[0]}"
        else:
            response += "No relevant documents found."
        
        return {
            "agent_id": "AGENT-B-RAG",
            "task_id": task.get("task_id", "UNKNOWN"),
            "response": response,
            "tool_calls": ["knowledge_base_retrieval"],
            "retrieved_evidence": relevant_docs,
            "execution_status": "success",
        }
