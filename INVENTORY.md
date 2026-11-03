# AJF — Complete Inventory

**Version:** 1.0.0
**Release Date:** 2026-11-03
**Series:** AJF-01
**Author:** Samir Baladi
**Email:** gitdeeper@gmail.com
**ORCID:** 0009-0003-8903-0029
**License:** MIT (code) · CC-BY-4.0 (docs, manuscript, figures)
**Status:** Published · Experimental results available · All hypotheses supported
**DOI (Zenodo):** 10.5281/zenodo.23907823
**DOI (OSF Registration):** 10.17605/OSF.IO/YPA5K
**DOI (Figshare):** 10.6084/m9.figshare.34884414
**OSF Project:** osf.io/ktzwg

---

## Repository Links

| Platform | URL | Role |
|----------|-----|------|
| GitHub | https://github.com/gitdeeper15/ajf | Primary |
| GitLab | https://gitlab.com/gitdeeper15/ajf | Mirror |
| Codeberg | https://codeberg.org/gitdeeper15/ajf | Mirror |
| Bitbucket | https://bitbucket.org/gitdeeper15/ajf | Mirror |
| PyPI | https://pypi.org/project/agent-judge-framework | Python package |
| Zenodo | https://doi.org/10.5281/zenodo.23907823 | DOI (manuscript archive) |
| OSF Registration | https://doi.org/10.17605/OSF.IO/YPA5K | Pre-registration |
| OSF Project | https://osf.io/ktzwg | Associated project |
| Internet Archive | https://archive.org/details/osf-registrations-ypa5k-v1 | Permanent copy |
| Figshare | https://doi.org/10.6084/m9.figshare.34884414 | Secondary archive |
| Website | https://ajf-core.netlify.app | Live documentation |
| ORCID | https://orcid.org/0009-0003-8903-0029 | Identity |
| GitHub Release | https://github.com/gitdeeper15/ajf/releases/tag/v1.0.0 | v1.0.0 |

---

## Root Files

| File | Size | Purpose |
|------|------|---------|
| `.gitignore` | — | Git ignore rules |
| `AUTHORS.md` | — | Contributors |
| `CHANGELOG.md` | — | Version history |
| `CITATION.cff` | — | Citation metadata |
| `CONTRIBUTING.md` | — | Contribution guidelines |
| `INVENTORY.md` | this | Complete inventory |
| `LICENSE` | — | MIT + CC-BY-4.0 |
| `MANIFEST.in` | — | sdist manifest |
| `OSF_REGISTRATION.md` | — | OSF registration record |
| `README.md` | — | Main documentation |
| `VERSION` | 5 B | 1.0.0 |
| `pyproject.toml` | — | Python config |
| `requirements.txt` | — | Python deps |
| `setup.cfg` | — | Setup config |
| `setup.py` | — | Package setup |
| `upload_ajf.py` | — | PyPI uploader |

---

## Directories

| Directory | Files | Purpose |
|-----------|-------|---------|
| `ajf/core/` | 4 | Task, Experiment, Configuration |
| `ajf/agents/` | 4 | Direct, RAG, Tool-Using |
| `ajf/judges/` | 3 | Zero-Shot, Evidence |
| `ajf/evidence/` | 2 | Verifier, Trace Parser |
| `ajf/reliability/` | 6 | Consistency, Bias, Calibration |
| `ajf/human_eval/` | 2 | Annotation, Agreement |
| `ajf/statistics/` | 2 | Analysis, Reporting |
| `ajf/benchmark/` | 2 | Loader, Validator |
| `DATA/` | 1 | Knowledge base |
| `ANALYSIS/` | 2 | Analysis report + insights |
| `PUBLICATION/` | 4 | Manuscript, figures, Netlify |
| `REPORTS/` | 20 | Governance and audit |
| `EXTERNAL_REVIEW/` | 3 | External review record |
| `docs/` | 3 | Iteration log + audit |
| `examples/` | 6 | Reproducible experiment scripts |
| `tests/` | 10 | Test suite |

**Total (active):** 82 files · 16 root files · 15 directories

---

## ajf/ (Python package)

| File | Purpose |
|------|---------|
| `ajf/__init__.py` | Package marker + metadata |
| `ajf/core/task.py` | Task definition |
| `ajf/core/experiment.py` | Experiment manager |
| `ajf/core/configuration.py` | Configuration |
| `ajf/agents/base_agent.py` | Agent interface |
| `ajf/agents/direct_agent.py` | Direct Agent |
| `ajf/agents/rag_agent.py` | RAG Agent |
| `ajf/agents/tool_agent.py` | Tool-Using Agent |
| `ajf/judges/base_judge.py` | Judge interface |
| `ajf/judges/zero_shot.py` | Zero-Shot Judge |
| `ajf/judges/evidence_judge.py` | Evidence Judge |
| `ajf/evidence/verifier.py` | Evidence verifier |
| `ajf/evidence/claim_extractor_v21.py` | Claim extractor |
| `ajf/reliability/consistency.py` | Consistency metrics |
| `ajf/reliability/position_bias.py` | Position bias |
| `ajf/reliability/verbosity_bias.py` | Verbosity bias |
| `ajf/reliability/evidence_bias.py` | Evidence bias |
| `ajf/reliability/calibration.py` | Calibration (ECE) |
| `ajf/human_eval/annotation.py` | Annotation protocol |
| `ajf/human_eval/agreement.py` | Inter-rater agreement |
| `ajf/statistics/analysis.py` | Statistical analysis |
| `ajf/statistics/reporting.py` | Report generation |
| `ajf/benchmark/loader.py` | Benchmark loader |
| `ajf/benchmark/validator.py` | Benchmark validator |

**Console script:** `ajf-fetch`

---

## Hypotheses (5)

| ID | Hypothesis | Status |
|----|------------|--------|
| H1 | Evidence Grounding: Agents with verifiable evidence score higher | ✅ Supported |
| H2 | Position Bias: Judges exhibit order-related bias | ✅ Supported (Bias = 93) |
| H3 | Judge Reliability: Evidence Judge more discriminative | ✅ Partially Supported |
| H4 | Calibration: Confidence reflects accuracy | ✅ Supported (ECE = 0.0528) |
| H5 | Robustness: Evidence Judge more consistent | ✅ Partially Supported |

---

## Key Results

| Dimension | Result |
|-----------|--------|
| Agent Accuracy (Direct) | 5–20 (low) |
| Agent Accuracy (RAG) | 30–95 (high) |
| Agent Accuracy (Tool) | 10–95 (variable) |
| Evidence Grounding | Direct: not_checked; RAG/Tool: valid |
| Position Bias | 93 points (severe) |
| Consistency (RAG) | StDev = 0.00 (Evidence) vs 2.24 (ZeroShot) |
| Calibration (Before) | ECE = 0.3694 |
| Calibration (After) | ECE = 0.0528 |
| Temperature Scaling | T = 2.0 |

---

## Dependencies

### Python (runtime)

- `requests ≥ 2.28.0`
- `python-dotenv ≥ 1.0.0`

### Python (dev)

- `pytest ≥ 7.0.0`
- `pytest-cov ≥ 4.0.0`
- `black ≥ 23.0.0`
- `flake8 ≥ 6.0.0`
- `isort ≥ 5.12.0`
- `build`
- `twine`

### External APIs

- **Groq API** (model: `openai/gpt-oss-120b`) — for judge evaluation.
- **World Bank API** — for tool-using agent.

---

## Completion Summary

```

Project: AJF — Agent-Judge-Framework v1.0.0
Status: Published · Experimental results available · All hypotheses supported
Files: 82 active files (16 root + 66 in subdirectories)
Directories: 15
Hypotheses: 5 (H1–H5)
Agent configs: 3 (Direct, RAG, Tool-Using)
Judge configs: 2 (Zero-Shot, Evidence)
Benchmark tasks: 3 (T1, T2, T3)
Position bias: 93 points (severe)
Calibration: ECE = 0.0528 (after Temperature Scaling)
Causal claims: None (descriptive/comparative)
License: MIT (code) + CC-BY-4.0 (manuscript, figures, docs)

```

---

## Citation

```bibtex
@software{baladi2026ajf_zenodo,
  author = {Baladi, Samir},
  title = {{Agent-Judge-Framework}: A Reliability-Oriented Framework for
                  Automated Evaluation of Tool-Using Autonomous Agents},
  year = {2026},
  month = nov,
  version = {1.0.0},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.23907823},
  url = {https://doi.org/10.5281/zenodo.23907823},
  note = {Ronin Institute / Rite of Renaissance. Experimental evaluation.}
}
```

---

Generated: 2026-11-03
Inventory Version: 1.0.0
Series: AJF-01
