"""Experiment Manager."""
from ajf.core.task import Task
from ajf.agents.base_agent import BaseAgent
from ajf.judges.base_judge import BaseJudge
from typing import Dict, Any
import json

class Experiment:
    """Manages the execution of a single experiment."""
    
    def __init__(self, experiment_id: str):
        self.experiment_id = experiment_id
    
    def run(self, task: Task, agent: BaseAgent, judge: BaseJudge) -> Dict[str, Any]:
        """Run a single task through an agent and a judge."""
        task_dict = task.__dict__
        
        # 1. Agent executes
        agent_output = agent.execute(task_dict)
        
        # 2. Judge evaluates
        judge_output = judge.evaluate(task_dict, agent_output)
        
        # 3. Collect results
        result = {
            "experiment_id": self.experiment_id,
            "task_id": task.task_id,
            "agent_output": agent_output,
            "judge_output": judge_output,
        }
        
        return result
