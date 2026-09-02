# Aminoglycoside Hartford Nomogram

> **Domain:** Clinical Pharmacology & Precision Pharmacotherapy  
> **Reference Guidelines & Standards:** `CPIC Guidelines & FDA Table of Pharmacogenomic Biomarkers`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Extended-interval aminoglycoside enrichment features for
aminoglycoside-hartford-nomogram.

Implements the top three items from specifications:

1. Hartford extended-interval nomogram interval selection (Nicolau et al.,
   1995): gentamicin/tobramycin 7 mg/kg, random level drawn 6-14 h after the
   start of a 30-minute infusion; CrCl >= 60 mL/min required. The published
   q24h/q36h and q36h/q48h boundary curves are reproduced from their
   digitized anchor points and interpolated log-linearly (first-order decay).

2. Amikacin nomogram extension: once-daily amikacin 20 mg/kg with the
   institutional adaptation of doubling the gentamicin/tobramycin cutoffs
   (proportional to the doubled mg/kg dose).

3. Composite nephrotoxicity risk score combining baseline CrCl, age,
   concurrent vancomycin, therapy duration, and sepsis/shock to set the
   level-monitoring cadence.

Author: Dr. Abu Suraih Sakhri
License: MIT

Hartford Once-Daily Aminoglycoside Nomogram
Plots 6-to-14 hour post-dose gentamicin/tobramycin levels on Hartford nomogram for 24h/36h/48h interval selection.

Zero-dependency Python implementation with single and batch evaluation.
Author: Dr. Abu Suraih Sakhri
License: MIT

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`NomogramResult`** — dedicated module for nomogram result evaluation and state verification.

---

## 📐 Mathematical Formulation & Logic

```text
  score = primary_val
  rounded_score = round(score, 2)
  res = calculate_metrics(**kwargs)
  calc_res = calculate_metrics(**r)
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --task-id <value> --target <value> --primary <value> --secondary <value>
```

### Parameter Reference
- `--task-id`: Specifies input measurement or parameter value.
- `--target`: Specifies input measurement or parameter value.
- `--primary`: Specifies input measurement or parameter value.
- `--secondary`: Specifies input measurement or parameter value.
- `--critical`: Specifies input measurement or parameter value.
- `--status`: Specifies input measurement or parameter value.
- `--input`: Specifies input measurement or parameter value.
- `--output`: Specifies input measurement or parameter value.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Parameter / observation metric | Required |
| `v1` | Parameter / observation metric | Required |
| `v2` | Parameter / observation metric | Required |
| `v3` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t aminoglycoside-hartford-nomogram .
docker run -p 8000:8000 aminoglycoside-hartford-nomogram
```
