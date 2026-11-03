"""Run experiments with all three agents and both judges."""
import json
from ajf.core.task import Task
from ajf.core.experiment import Experiment
from ajf.agents.direct_agent import DirectAgent
from ajf.agents.rag_agent import RAGAgent
from ajf.agents.tool_agent import ToolAgent
from ajf.judges.zero_shot import ZeroShotJudge
from ajf.judges.evidence_judge import EvidenceJudge

# 1. Define a Task
task = Task(
    task_id="TASK-001",
    description="Retrieve the latest population estimate for Morocco from World Bank WDI.",
    expected_outcome="Morocco population (2024): ~37.5 million",
    reference_source="World Bank WDI (SP.POP.TOTL)",
    required_tools=["world_bank_api"],
)

# 2. Initialize Agents
agents = {
    "Direct": DirectAgent(),
    "RAG": RAGAgent(),
    "Tool": ToolAgent(),
}

# 3. Initialize Judges
judges = {
    "ZeroShot": ZeroShotJudge(),
    "Evidence": EvidenceJudge(),
}

# 4. Run all combinations
experiment = Experiment(experiment_id="AJF-EXP-001")
results = []

for agent_name, agent in agents.items():
    for judge_name, judge in judges.items():
        print(f"\n=== Running: {agent_name} Agent + {judge_name} Judge ===")
        result = experiment.run(task, agent, judge)
        results.append(result)
        print(json.dumps(result, indent=2))

# 5. Save all results
with open("EXPERIMENTS/results/batch_001.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n✅ All experiments completed. Results saved to EXPERIMENTS/results/batch_001.json")
