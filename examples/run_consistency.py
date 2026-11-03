"""Run the same experiment 5 times to measure judge consistency."""
import json
import statistics
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

# 4. Run 5 repetitions
results = []
for run in range(1, 6):
    print(f"\n=== Repetition {run}/5 ===")
    for agent_name, agent in agents.items():
        for judge_name, judge in judges.items():
            exp = Experiment(experiment_id=f"AJF-CONSISTENCY-RUN-{run}")
            result = exp.run(task, agent, judge)
            result["run"] = run
            result["agent_name"] = agent_name
            result["judge_name"] = judge_name
            results.append(result)
            print(f"  {agent_name:8} | {judge_name:10} | Score: {result['judge_output']['score']:3}")

# 5. Calculate Consistency (Variance per agent-judge pair)
print("\n=== Consistency Analysis (Variance) ===")
pairs = {}
for r in results:
    key = (r["agent_name"], r["judge_name"])
    if key not in pairs:
        pairs[key] = []
    pairs[key].append(r["judge_output"]["score"])

for (agent, judge), scores in pairs.items():
    mean = statistics.mean(scores)
    stdev = statistics.stdev(scores) if len(scores) > 1 else 0.0
    print(f"{agent:8} | {judge:10} | Mean: {mean:5.1f} | StDev: {stdev:5.2f} | Scores: {scores}")

# 6. Save results
with open("EXPERIMENTS/results/consistency.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n✅ Consistency test completed. Results saved to EXPERIMENTS/results/consistency.json")
