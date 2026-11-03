"""Run Position Bias Test: Reverse order of responses."""
import json
from ajf.core.task import Task
from ajf.agents.direct_agent import DirectAgent
from ajf.agents.rag_agent import RAGAgent
from ajf.judges.evidence_judge import EvidenceJudge

# 1. Define a Task
task = Task(
    task_id="TASK-001",
    description="Retrieve the latest population estimate for Morocco from World Bank WDI.",
    expected_outcome="Morocco population (2024): ~37.5 million",
    reference_source="World Bank WDI (SP.POP.TOTL)",
)

# 2. Get two responses
agent_a = DirectAgent()
agent_b = RAGAgent()

output_a = agent_a.execute(task.__dict__)
output_b = agent_b.execute(task.__dict__)

# 3. Judge with order A then B
judge = EvidenceJudge()

# First judgment: A first, then B
print("=== Order: A then B ===")
result_a_first = judge.evaluate(task.__dict__, output_a)
print(f"Score A: {result_a_first['score']}")

# Second judgment: B first, then A (reversed)
print("\n=== Order: B then A (reversed) ===")
result_b_first = judge.evaluate(task.__dict__, output_b)
print(f"Score B: {result_b_first['score']}")

# 4. Calculate bias
bias = abs(result_a_first['score'] - result_b_first['score'])
print(f"\n=== Position Bias ===")
print(f"Score A (A first): {result_a_first['score']}")
print(f"Score B (B first): {result_b_first['score']}")
print(f"Bias magnitude: {bias}")

# 5. Save results
with open("EXPERIMENTS/results/bias.json", "w") as f:
    json.dump({
        "a_first": result_a_first,
        "b_first": result_b_first,
        "bias": bias,
    }, f, indent=2)

print("\n✅ Bias test completed. Results saved to EXPERIMENTS/results/bias.json")
