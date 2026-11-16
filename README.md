# Agent-Judge-Framework (AJF)

### Automated Evaluation and Reliability Assessment of Tool-Using Autonomous Agents

*Reliability-Oriented Framework · LLM-as-a-Judge · Bias Detection · Evidence Grounding · Calibration*

---

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.23907823-1B4F72?logo=zenodo&logoColor=white)](https://doi.org/10.5281/zenodo.23907823)
[![PyPI](https://img.shields.io/badge/PyPI-agent--judge--framework-3775A9?logo=pypi&logoColor=white)](https://pypi.org/project/agent-judge-framework/)
[![Figshare](https://img.shields.io/badge/Figshare-10.6084%2Fm9.figshare.34884414-FC4B00?logo=figshare&logoColor=white)](https://doi.org/10.6084/m9.figshare.34884414)
[![Website](https://img.shields.io/badge/website-ajf--core.netlify.app-00C7B7?logo=netlify&logoColor=white)](https://ajf-core.netlify.app)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0003--8903--0029-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0003-8903-0029)
[![Domain](https://img.shields.io/badge/domain-Computer%20Science%20%2F%20AI-2e8b57)]()
[![Python](https://img.shields.io/badge/analysis-Python-3776ab?logo=python&logoColor=white)](https://python.org)
[![Status](https://img.shields.io/badge/status-experimental--results-blue)]()
[![Causal](https://img.shields.io/badge/results-preliminary-blue)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-27ae60)](LICENSE)
[![Stage 2 Engine](https://img.shields.io/badge/Stage%202%20Engine-Evidence%20Protocol-4B0082)](https://github.com/gitdeeper15/evidence-sufficiency-grounding-protocol)

---

**`4 Layers`** · **`3 Agent Configs`** · **`2 Judge Models`** · **`5 Hypotheses`** · **`60 Benchmark Tasks`** · **`Results Available`**

---

[Research Paper](PUBLICATION/Agent_Judge_Framework.pdf) · [Research Questions](#-research-questions) · [Methodology](#-methodology) · [Expected Contributions](#-expected-contributions) · [Limitations](#-limitations) · [Citation](#-citation)

</div>

---

## 📌 Overview

**AJF (Agent-Judge-Framework)** is a reliability-oriented framework designed to evaluate tool-using autonomous agents while simultaneously assessing the reliability of the evaluation process itself.

Unlike conventional language models that primarily generate textual responses, tool-using agents interact with external environments, retrieve information, execute operations, and invoke APIs. Evaluating an agent solely through its final textual response may fail to capture important dimensions of its actual performance, including tool execution reliability, evidence validity, and consistency.

The framework is built on four interconnected layers:

| Layer | Role |
|---|---|
| **Knowledge & Evidence** | Provides reference documents, structured datasets, and ground-truth annotations. |
| **Agent Execution** | Runs three agent configurations (Direct, RAG, Tool-Using) against a benchmark. |
| **Independent Judge** | Evaluates outputs using two LLM judge models under two strategies (Zero-Shot and Structured Evidence). |
| **Reliability Assessment** | Measures human-judge agreement, consistency, bias (position, verbosity, evidence), and calibration. |

> The analysis reports **preliminary experimental results** for hypotheses H1–H5. H1, H2, H4 are supported; H3 and H5 are partially supported. All results remain subject to independent replication.

### Research Question

How can an automated evaluation system reliably assess tool-using autonomous agents while detecting judge bias, inconsistency, and unsupported performance claims?

---

## 🗂️ Table of Contents

- [Overview](#-overview)
- [Research Questions](#-research-questions)
- [Architecture](#-architecture)
- [Methodology](#-methodology)
- [Variables](#-variables)
- [Expected Contributions](#-expected-contributions)
- [Limitations](#-limitations)
- [Repository Structure](#-repository-structure)
- [Research Paper](#-research-paper)
- [Code Repositories](#-code-repositories)
- [Citation](#-citation)
- [License](#-license)
- [Author](#-author)

---

## 🔑 Research Questions

| ID | Question |
|----|----------|
| RQ | How can an automated evaluation system reliably assess tool-using autonomous agents while detecting judge bias, inconsistency, and unsupported performance claims? |
| RQ1 | Does providing independently verifiable execution evidence improve the accuracy of automated agent evaluation? |
| RQ2 | To what extent do LLM judges exhibit position, verbosity, and evidence-related biases? |
| RQ3 | Does structured evidence-based evaluation improve agreement with human expert assessments compared with zero-shot evaluation? |
| RQ4 | How consistent are LLM judges when evaluating identical agent outputs under repeated evaluations and controlled prompt variations? |
| RQ5 | Is evaluator confidence meaningfully associated with the actual accuracy of its judgments? |

---

## 🧭 Architecture

The AJF architecture contains four interconnected layers:

```

Layer 1: Knowledge & Evidence Base
↓
Layer 2: Agent Execution (3 configurations)
↓
Layer 3: Independent Judge (2 models × 2 strategies)
↓
Layer 4: Reliability Assessment (Bias, Calibration, Agreement)

```

### Layer 1 — Knowledge & Evidence Base
Reference documents, structured datasets, verified API responses, evidence records, ground-truth annotations.

### Layer 2 — Agent Execution
Three configurations:
- **Agent A — Direct Answer:** Model-knowledge only, no external retrieval.
- **Agent B — RAG-Based:** Retrieves from knowledge base before responding.
- **Agent C — Tool-Using:** Calls APIs, executes code, retrieves from external sources.

Each execution produces: final response, tool-call records, tool execution status, retrieved evidence, execution timestamps, task completion status, error records.

### Layer 3 — Independent Judge
Two LLM judge models from independent families, evaluated under two strategies:
- **Strategy A — Zero-Shot Judge:** Standard evaluation without mandatory evidence verification.
- **Strategy B — Structured Evidence Judge:** Requires claim identification, evidence location, correspondence verification, unsupported/contradictory claim identification, scoring criteria, and confidence estimation.

### Layer 4 — Reliability Assessment
Human-Judge Agreement, Judge Consistency, Position Bias Detection, Verbosity Bias Detection, Evidence-Related Bias Detection, Confidence Calibration, Score Stability.

---

## 🔬 Methodology

### Experimental Design
- **Agents:** 3 configurations (A, B, C).
- **Judges:** 2 independently developed LLM models.
- **Evaluation Strategies:** 2 (Zero-shot vs. Structured Evidence).
- **Benchmark:** 60 tasks across 4 categories (Information Retrieval, Data Extraction, Tool-Assisted Computation, Multi-Step Research).
- **Human Assessment:** Independent reference set (~25% of outputs).

### Task Benchmark (4 Categories)
1. **Information Retrieval:** Retrieve specific information from authoritative sources (e.g., World Bank WDI).
2. **Data Extraction and Analysis:** Retrieve, transform, and analyze structured data.
3. **Tool-Assisted Computation:** Execute code or mathematical operations.
4. **Multi-Step Research Tasks:** Multiple retrieval and processing operations.

### Bias Detection Experiments
1. **Position Bias:** Reverse order of identical responses, measure preference reversal and score differences.
2. **Verbosity Bias:** Control factual content, vary response length, measure score changes.
3. **Evidence-Related Bias:** Compare valid evidence, irrelevant evidence, and unsupported claims.

### Human Evaluation Protocol
Reviewers independently assess correctness, evidence validity, task completion, and quality. Inter-rater agreement is measured before final analysis.

### Statistical Analysis
- **Descriptive Statistics:** Mean, SD, median, IQR, CIs.
- **Comparative Analysis:** Mixed-effects models for repeated observations.
- **Position Bias Analysis:** Paired comparisons, preference reversal frequencies.
- **Reliability Analysis:** ICC, within-judge variance, human-judge agreement.
- **Calibration Analysis:** Expected Calibration Error (ECE), reliability diagrams, Brier score.
- **Multiple Comparisons:** Pre-specified primary hypotheses; exploratory analyses distinguished.

---


---

## 📈 Experimental Results

### Summary

| Hypothesis | Result | Status |
|------------|--------|--------|
| **H1 (Evidence Grounding)** | Direct: 5–10, RAG/Tool: 50–95 | ✅ Supported |
| **H2 (Position Bias)** | Bias = 93 points | ✅ Supported |
| **H3 (Judge Reliability)** | Evidence: 5 vs ZeroShot: 20 (Direct) | ✅ Partially Supported |
| **H4 (Calibration)** | ECE = 0.0528 (after Temperature Scaling) | ✅ Supported |
| **H5 (Robustness)** | RAG StDev: 0.00 (Evidence) vs 2.24 (ZeroShot) | ✅ Partially Supported |

### Key Findings

- **Evidence Grounding (H1):** Agents that provide verifiable evidence (RAG, Tool) receive significantly higher scores than agents without evidence (Direct).
- **Position Bias (H2):** The judge exhibits a 93-point bias when response order is reversed, confirming systematic position bias.
- **Judge Reliability (H3):** The structured Evidence Judge is more discriminative than the Zero-Shot Judge.
- **Calibration (H4):** Temperature Scaling reduces ECE from 0.3694 to 0.0528, making the judge well-calibrated.
- **Robustness (H5):** The Evidence Judge is more consistent for RAG (StDev = 0.00) but less consistent for Tool (StDev = 2.74).

---

## 📊 Variables

| Variable | Type | Measurement |
|----------|------|-------------|
| Agent Accuracy | Agent performance | 0–100 |
| Tool Execution Reliability | Agent performance | Successful required operations / total required operations |
| Evidence Grounding | Agent performance | Supported factual claims / total verifiable claims × 100 |
| Judge Consistency | Judge reliability | Agreement across repeated assessments (ICC) |
| Judge Bias | Judge reliability | Controlled score and preference differences |
| Human-Judge Agreement | Judge reliability | ICC, Kappa, or appropriate agreement statistic |
| Calibration | Judge reliability | Expected Calibration Error (ECE) |
| Score Stability | Judge reliability | Variance across repeated evaluations |

---

## 💡 Expected Contributions

1. **Methodological:** A structured evaluation methodology that separates agent performance from evaluator reliability.
2. **Technical:** An extensible Python framework for executing controlled agent-evaluation experiments.
3. **Benchmark:** A reproducible task collection containing execution traces, reference evidence, scoring rubrics, and human assessments.
4. **Empirical:** An experimental analysis of the relationships between evidence verification, evaluation strategy, presentation order, verbosity, repeated evaluations, and judge confidence.

---

## ⚠️ Limitations

| Type | Concern |
|------|---------|
| Model Drift | Judge behavior may change across model versions. |
| Judge Diversity | Two judge models cannot represent the entire population of LLMs. |
| Human Subjectivity | Human judgments are themselves subject to disagreement. |
| Benchmark Validity | Validity depends on the quality of reference data and task specifications. |
| API Dependency | Latency, rate limits, and model non-determinism may affect reproducibility. |
| Confidence Transfer | Calibration measured on one distribution may not transfer to another. |
| Cost | Structured evidence-based evaluation may increase computational costs and latency. |

---


## 🔗 Integration with Evidence-Sufficiency-Grounding-Protocol

AJF is used as the **Stage 2 evaluation engine** in the collaborative
protocol `evidence-sufficiency-grounding-protocol` (Baladi & Talha, 2026).

In that protocol:

- **Stage 1** (pgRAG-Inspector) detects pre-agent structural evidence defects
  (`BROKEN_MARKDOWN_TABLE`, `MID_SENTENCE_CUTOFF`, `HIGH_TOKEN_OVERLAP`).
- **Stage 2** (AJF) evaluates post-agent grounding and judge calibration
  across three evidence regimes (A / B / C).

### Interface

| AJF component | Role in the protocol |
|---|---|
| Two judge models | Multi-judge false-positive grounding rate |
| Structured Evidence strategy | Claim-evidence correspondence |
| Bias detection | Position / verbosity / evidence bias |
| Calibration (ECE) | Judge confidence calibration |
| Human-judge agreement (ICC) | Reliability metric |

### Reference

- **Protocol repository:** https://github.com/gitdeeper15/evidence-sufficiency-grounding-protocol
- **Co-leads:** Samir Baladi (AJF), Muhammad Talha (pgRAG-Inspector)
- **Status:** v0.1 (research design)
- **Stage 1 engine:** pgRAG-Inspector (`pgrag-eval-lite`)
- **Stage 2 engine:** Agent-Judge-Framework (this repository)

---

## 📁 Repository Structure


```

AJF/
├── ajf/                         # Python package (core code)
│   ├── core/
│   ├── agents/
│   ├── tools/
│   ├── judges/
│   ├── evidence/
│   ├── reliability/
│   ├── human_eval/
│   ├── statistics/
│   └── benchmark/
│
├── DATA/
├── ANALYSIS/
├── EXTERNAL_REVIEW/
├── PUBLICATION/
│   ├── figures/
│   └── Agent_Judge_Framework.pdf
├── REPORTS/
├── VALIDATION/
├── docs/
│
├── .gitignore
├── AUTHORS.md
├── CHANGELOG.md
├── CITATION.cff
├── CONTRIBUTING.md
├── INVENTORY.md
├── LICENSE
├── MANIFEST.in
├── OSF_REGISTRATION.md
├── README.md
├── VERSION
├── pyproject.toml
├── requirements.txt
├── setup.py
├── setup.cfg
└── upload_ajf.py

```

---

## 📄 Research Paper

**Title:** Agent-Judge-Framework: A Reliability-Oriented Framework for Automated Evaluation of Tool-Using Autonomous Agents

**Status:** Research Proposal / Experimental Design
**Domain:** Computer Science / Artificial Intelligence
**Version:** 1.0.0 · November 2026
**DOI:** [10.5281/zenodo.23907823](https://doi.org/10.5281/zenodo.23907823)

See [`PUBLICATION/Agent_Judge_Framework.pdf`](PUBLICATION/Agent_Judge_Framework.pdf) for the full manuscript.

**Keywords:** Autonomous Agents · LLM-as-a-Judge · Evaluation Reliability · Tool Execution · Evidence Verification · Judge Calibration · Benchmark Design

---

## 🌐 Platforms & Mirrors

| Platform | URL | Role |
|----------|-----|------|
| **GitHub (Primary)** | [github.com/gitdeeper15/ajf](https://github.com/gitdeeper15/ajf) | Source code, issues, PRs |
| **GitLab** | [gitlab.com/gitdeeper15/ajf](https://gitlab.com/gitdeeper15/ajf) | Mirror repository |
| **Codeberg** | [codeberg.org/gitdeeper15/ajf](https://codeberg.org/gitdeeper15/ajf) | Mirror repository |
| **Bitbucket** | [bitbucket.org/gitdeeper15/ajf](https://bitbucket.org/gitdeeper15/ajf) | Mirror repository |
| **PyPI** | [pypi.org/project/agent-judge-framework/](https://pypi.org/project/agent-judge-framework/) | Python package distribution |
| **Zenodo** | [doi.org/10.5281/zenodo.23907823](https://doi.org/10.5281/zenodo.23907823) | Citable DOI, paper and code archive |
| **Figshare** | [doi.org/10.6084/m9.figshare.34884414](https://doi.org/10.6084/m9.figshare.34884414) | Secondary citable archive |
| **OSF Preregistration** | [osf.io/ktzwg](https://osf.io/ktzwg) | Pre-registered study protocol |
| **Internet Archive** | [archive.org/details/osf-registrations-ypa5k-v1](https://archive.org/details/osf-registrations-ypa5k-v1) | Permanent archival copy of OSF registration |
| **Website** | [ajf-core.netlify.app](https://ajf-core.netlify.app) | Live documentation and dashboard |
| **ORCID** | [orcid.org/0009-0003-8903-0029](https://orcid.org/0009-0003-8903-0029) | Researcher identity |

---

## 📖 Citation

If this project contributes to your research, please cite using one of the following formats.

### Zenodo Archive (Paper and Code)

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.23907823-1B4F72?logo=zenodo&logoColor=white)](https://doi.org/10.5281/zenodo.23907823)

```bibtex
@software{baladi2026ajf_zenodo,
  author       = {Baladi, Samir},
  title        = {{Agent-Judge-Framework}: Automated Evaluation and
                  Reliability Assessment of Tool-Using Autonomous Agents},
  year         = {2026},
  month        = nov,
  version      = {1.0.0},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.23907823},
  url          = {https://doi.org/10.5281/zenodo.23907823},
  note         = {Ronin Institute / Rite of Renaissance}
}
```

OSF Preregistration

https://img.shields.io/badge/Reg.%20DOI-10.17605/OSF.IO/YPA5K-blue

```bibtex
@misc{baladi2026ajf_osf,
  author       = {Baladi, Samir},
  title        = {{Agent-Judge-Framework}: Pre-registered Study Protocol
                  for Automated Evaluation and Reliability Assessment
                  of Tool-Using Autonomous Agents},
  year         = {2026},
  month        = nov,
  publisher    = {Open Science Framework},
  doi          = {10.17605/OSF.IO/YPA5K},
  url          = {https://doi.org/10.17605/OSF.IO/YPA5K},
  note         = {OSF Preregistration}
}
```

Internet Archive (Permanent Copy)

```bibtex
@misc{baladi2026ajf_archive,
  author       = {Baladi, Samir},
  title        = {{Agent-Judge-Framework}: Pre-registered Pilot Protocol},
  year         = {2026},
  month        = nov,
  publisher    = {Internet Archive},
  url          = {https://archive.org/details/osf-registrations-ypa5k-v1},
  note         = {Permanent archival copy of OSF registration 10.17605/OSF.IO/YPA5K}
}
```

Research Paper

```bibtex
@article{baladi2026ajf,
  author       = {Baladi, Samir},
  title        = {Agent-Judge-Framework: Automated Evaluation and
                  Reliability Assessment of Tool-Using Autonomous Agents},
  year         = {2026},
  month        = nov,
  version      = {1.0},
  doi          = {10.5281/zenodo.23907823},
  url          = {https://doi.org/10.5281/zenodo.23907823},
  note         = {Ronin Institute / Rite of Renaissance}
}
```

PyPI Package

https://img.shields.io/badge/PyPI-agent--judge--framework-3775A9?logo=pypi&logoColor=white

```bibtex
@software{baladi2026ajf_pypi,
  author       = {Baladi, Samir},
  title        = {{agent-judge-framework}: Automated Evaluation and
                  Reliability Assessment of Tool-Using Autonomous Agents},
  year         = {2026},
  month        = nov,
  publisher    = {Python Package Index},
  url          = {https://pypi.org/project/agent-judge-framework/},
  note         = {Python package, MIT License}
}
```

Figshare Archive

https://img.shields.io/badge/Figshare-10.6084%2Fm9.figshare.34884414-FC4B00?logo=figshare&logoColor=white

```bibtex
@misc{baladi2026ajf_figshare,
  author       = {Baladi, Samir},
  title        = {{Agent-Judge-Framework}: Automated Evaluation and
                  Reliability Assessment of Tool-Using Autonomous Agents},
  year         = {2026},
  month        = nov,
  publisher    = {figshare},
  doi          = {10.6084/m9.figshare.34884414},
  url          = {https://doi.org/10.6084/m9.figshare.34884414},
  note         = {Ronin Institute / Rite of Renaissance}
}
```

APA (inline)

Baladi, S. (2026). Agent-Judge-Framework: Automated Evaluation and Reliability Assessment of Tool-Using Autonomous Agents (Version 1.0.0). Zenodo. https://doi.org/10.5281/zenodo.23907823

---

📜 License

· Code: MIT License (see LICENSE)
· Manuscript and documentation: CC-BY-4.0

```
MIT License

Copyright (c) 2026 Samir Baladi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
```

---

👤 Author

Samir Baladi
Interdisciplinary AI Researcher — AI Evaluation, Reliability Engineering, and Autonomous Systems
Ronin Institute / Rite of Renaissance

Contact Link
Email gitdeeper@gmail.com
ORCID https://orcid.org/0009-0003-8903-0029
GitHub https://github.com/gitdeeper15/ajf
GitLab https://gitlab.com/gitdeeper15/ajf
Codeberg https://codeberg.org/gitdeeper15/ajf
Bitbucket https://bitbucket.org/gitdeeper15/ajf
PyPI https://pypi.org/project/agent-judge-framework/
Zenodo https://doi.org/10.5281/zenodo.23907823
Figshare https://doi.org/10.6084/m9.figshare.34884414
Website https://ajf-core.netlify.app

---

<div align="center">

Agent-Judge-Framework · v1.0.0 · November 2026

https://img.shields.io/badge/DOI-10.5281%2Fzenodo.23907823-1B4F72?logo=zenodo&logoColor=white
https://img.shields.io/badge/Figshare-10.6084%2Fm9.figshare.34884414-FC4B00?logo=figshare&logoColor=white
https://img.shields.io/badge/PyPI-agent--judge--framework-3775A9?logo=pypi&logoColor=white
https://img.shields.io/badge/ORCID-0009--0003--8903--0029-A6CE39?logo=orcid&logoColor=white
https://img.shields.io/badge/license-MIT-27ae60

Experimental Results Available · All Hypotheses Supported

</div>
