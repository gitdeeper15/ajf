# Contributing to AJF

**Agent-Judge-Framework — Automated Evaluation and Reliability Assessment of Tool-Using Autonomous Agents**

---

## Status

This project is a **research proposal and experimental design** (`v1.0.0`). The manuscript and the architecture are complete; the Python implementation and the benchmark are under active development.

Contributions at this stage are welcome in:

- **Implementation** of the four layers (Knowledge, Agent Execution, Independent Judge, Reliability Assessment).
- **Benchmark tasks** for the four categories (Information Retrieval, Data Extraction, Tool-Assisted Computation, Multi-Step Research).
- **Judge prompts** (Zero-Shot and Structured Evidence).
- **Bias experiments** (Position, Verbosity, Evidence-Related).
- **Calibration methods** (Expected Calibration Error, Reliability Diagrams).
- **Documentation** (clarity, examples, tutorials).

**Not accepted at this stage:**

- New analyses that change the proposed architecture without justification.
- Changes to the research questions or hypotheses without a documented rationale.
- Rewriting the manuscript's conclusions.

For extensions (new bias experiments, additional judge models, cross-domain generalization), open an issue first to discuss scope.

---

## Reporting Issues

Open an issue with:

- A one-sentence description.
- The affected file (e.g., `README.md`, `ajf/judges/zero_shot.py`).
- A minimal reproduction or screenshot.
- Expected vs. actual behavior.

---

## Submitting Changes

```bash
git checkout -b feature/short-description
# make changes
git commit -m "feat: short description"
git push origin feature/short-description
```

Then open a pull request. Each PR should address one concern.

---

Code Standards

Language Standard
Python PEP 8, black (88 chars), isort, flake8
Markdown markdownlint (MD013 disabled)
YAML yamllint

Reproducibility: every code change must be reproducible from the public data and the published Python package.

---

Data Provenance

Data under DATA/raw/ originates from:

· World Bank WDI — public domain (CC-BY-4.0), see .
· Morocco 2025 State of the Environment Report — cited per source terms.

Do not commit derived data that is not reproducible from the scripts in DATA/raw/.

---

Review Process

· All changes are reviewed by the maintainer (Samir Baladi).
· Changes to the manuscript, figures, or reported numbers require explicit documentation in CHANGELOG.md with rationale.

---

Contact

· Email: gitdeeper@gmail.com
· ORCID: https://orcid.org/0009-0003-8903-0029
· Zenodo DOI: https://doi.org/10.5281/zenodo.23907823
· PyPI: https://pypi.org/project/agent-judge-framework/
· Figshare: (Pending)
· Website: (Pending)

---

Thank you for helping improve the reliability of automated agent evaluation.
