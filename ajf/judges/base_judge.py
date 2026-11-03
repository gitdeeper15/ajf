"""Base interface for all judges."""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseJudge(ABC):
    """Abstract base class for judges."""
    
    @abstractmethod
    def evaluate(self, task: Dict[str, Any], agent_output: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the agent output and return scores."""
        pass
