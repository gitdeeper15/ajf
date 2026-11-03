"""Apply Temperature Scaling to improve calibration."""
import json
import statistics
from ajf.core.task import Task
from ajf.agents.direct_agent import DirectAgent
from ajf.agents.rag_agent import RAGAgent
from ajf.agents.tool_agent import ToolAgent
from ajf.judges.zero_shot import ZeroShotJudge
from ajf.judges.evidence_judge import EvidenceJudge

# 1. Define tasks
tasks = [
    Task(task_id="T1", description="What is the population of Morocco?", expected_outcome="~37.5 million", reference_source="World Bank WDI"),
    Task(task_id="T2", description="What is the GDP of Morocco?", expected_outcome="~$157 billion", reference_source="World Bank WDI"),
    Task(task_id="T3", description="What is the freshwater withdrawals of Morocco?", expected_outcome="10.573 billion m³", reference_source="World Bank WDI"),
]

# 2. Run experiments
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

# 3. Apply Temperature Scaling (simple version: scale confidence by 0.5)
def calibrate_confidence(conf, temperature=2.0):
    """Apply temperature scaling to confidence."""
    # Simple approximation: reduce confidence by temperature
    return conf / temperature

# 4. Calculate ECE before and after calibration
print("=== Before Calibration ===")
bins = {0.1: [], 0.2: [], 0.3: [], 0.4: [], 0.5: [], 0.6: [], 0.7: [], 0.8: [], 0.9: [], 1.0: []}
for r in results:
    conf = round(r["confidence"], 1)
    if conf in bins:
        bins[conf].append(r["score"])

ece_before = 0.0
total = len(results)
for conf, scores in bins.items():
    if scores:
        avg_score = statistics.mean(scores)
        weight = len(scores) / total
        ece_before += weight * abs(avg_score / 100 - conf)

print(f"ECE (Before): {ece_before:.4f}")

# 5. Apply calibration
print("\n=== After Calibration (Temperature Scaling) ===")
bins_after = {0.1: [], 0.2: [], 0.3: [], 0.4: [], 0.5: [], 0.6: [], 0.7: [], 0.8: [], 0.9: [], 1.0: []}
for r in results:
    cal_conf = calibrate_confidence(r["confidence"], temperature=2.0)
    bin_key = round(cal_conf, 1)
    if bin_key in bins_after:
        bins_after[bin_key].append(r["score"])

ece_after = 0.0
for conf, scores in bins_after.items():
    if scores:
        avg_score = statistics.mean(scores)
        weight = len(scores) / total
        ece_after += weight * abs(avg_score / 100 - conf)

print(f"ECE (After):  {ece_after:.4f}")

# 6. Save results
with open("EXPERIMENTS/results/calibration_fix.json", "w") as f:
    json.dump({
        "results": results,
        "ece_before": ece_before,
        "ece_after": ece_after,
        "temperature": 2.0,
    }, f, indent=2)

print("\n✅ Calibration fix completed. Results saved to EXPERIMENTS/results/calibration_fix.json")
