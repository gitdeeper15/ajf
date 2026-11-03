"""Task definition for AJF."""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Task:
    """A single benchmark task."""
    task_id: str
    description: str
    expected_outcome: str
    reference_source: str
    required_tools: List[str] = field(default_factory=list)
    verification_procedure: Optional[str] = None
    scoring_rubric: Optional[str] = None
