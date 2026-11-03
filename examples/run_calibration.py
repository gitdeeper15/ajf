"""Measure Calibration: Confidence vs. Accuracy."""
import json
import statistics
from ajf.core.task import Task
from ajf.agents.direct_agent import DirectAgent
from ajf.agents.rag_agent import RAGAgent
from ajf.agents.tool_agent import ToolAgent
from ajf.judges.zero_shot import ZeroShotJudge
from ajf.judges.evidence_judge import EvidenceJudge

# 1. Define multiple tasks (with reference_source)
tasks = [
    Task(
        task_id="T1",
        description="What is the population of Morocco?",
        expected_outcome="~37.5 million",
        reference_source="World Bank WDI (SP.POP.TOTL)",
    ),
    Task(
        task_id="T2",
        description="What is the GDP of Morocco?",
        expected_outcome="~$157 billion",
        reference_source="World Bank WDI (NY.GDP.MKTP.CD)",
    ),
    Task(
        task_id="T3",
        description="What is the freshwater withdrawals of Morocco?",
        expected_outcome="10.573 billion m³",
        reference_source="World Bank WDI (ER.H2O.FWTL.K3)",
    ),
]

# 2. Run all tasks with all agents and judges
agents = {"Direct": DirectAgent(), "RAG": RAGAgent(), "Tool": ToolAgent()}
judges = {"ZeroShot": ZeroShotJudge(), "Evidence": EvidenceJudge()}

results = []
for task in tasks:
    for agent_name, agent in agents.items():
        for judge_name, judge in judges.items():
            output = agent.execute(task.__dict__)
            judgment = judge.evaluate(task.__dict__, output)
            results.append({
                "task_id": task.task_id,
                "agent_name": agent_name,
                "judge_name": judge_name,
                "score": judgment["score"],
                "confidence": judgment["confidence"],
            })

# 3. Calculate Calibration (binned by confidence)
print("=== Calibration Analysis ===")
bins = {0.1: [], 0.2: [], 0.3: [], 0.4: [], 0.5: [], 0.6: [], 0.7: [], 0.8: [], 0.9: [], 1.0: []}
for r in results:
    conf = round(r["confidence"], 1)
    if conf in bins:
        bins[conf].append(r["score"])

# Calculate ECE (Expected Calibration Error)
ece = 0.0
total = len(results)
for conf, scores in bins.items():
    if scores:
        avg_score = statistics.mean(scores)
        weight = len(scores) / total
        ece += weight * abs(avg_score / 100 - conf)  # Normalize score to [0,1]
        print(f"Confidence {conf:0.1f}: {len(scores)} samples, Avg Score: {avg_score:5.1f}")

print(f"\nExpected Calibration Error (ECE): {ece:.4f}")
print("Lower ECE = better calibration")

# 4. Save results
with open("EXPERIMENTS/results/calibration.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n✅ Calibration test completed. Results saved to EXPERIMENTS/results/calibration.json")
