import json
from pathlib import Path
from datetime import datetime, timezone

from ajf.evidence.verifier_v16 import EvidenceVerifierV16

INPUT = Path("EXPERIMENTS/results/batch_001.json")
OUTPUT = Path(
    "EXPERIMENTS/results/v16_batch_001_report.json"
)

SPEC = {
    "country_code": "MA",
    "indicator": "SP.POP.TOTL",
    "year": 2024
}

records = json.loads(INPUT.read_text())

# Keep one output per unique agent.
unique_agents = {}

for item in records:
    output = item.get("agent_output", {})
    agent_id = output.get("agent_id")

    if agent_id and agent_id not in unique_agents:
        unique_agents[agent_id] = output

verifier = EvidenceVerifierV16()
results = []

for agent_id, agent_output in unique_agents.items():
    print(f"\nVERIFYING: {agent_id}")

    try:
        result = verifier.verify_source(
            agent_output,
            SPEC
        )

        results.append({
            "agent_id": agent_id,
            "result": result
        })

        print(json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        ))

    except Exception as exc:
        results.append({
            "agent_id": agent_id,
            "error": f"{type(exc).__name__}: {exc}"
        })
        print("ERROR:", exc)

report = {
    "experiment_id": "AJF-EXP-001",
    "task_id": "TASK-001",
    "verifier_version": EvidenceVerifierV16.VERSION,
    "test_timestamp": datetime.now(
        timezone.utc
    ).isoformat(),
    "input_file": str(INPUT),
    "input_record_count": len(records),
    "unique_agent_count": len(unique_agents),
    "verification_spec": SPEC,
    "results": results
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    json.dumps(report, indent=2, ensure_ascii=False)
)

print("\n================================")
print("REPORT SAVED:", OUTPUT)
print("UNIQUE AGENTS:", len(unique_agents))
print("================================")
