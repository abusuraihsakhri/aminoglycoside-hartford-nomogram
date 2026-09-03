# Hartford Once-Daily Aminoglycoside Nomogram

A pure Python clinical pharmacokinetics and therapeutic drug monitoring (TDM) framework implementing the Hartford extended-interval nomogram (Nicolau et al., *Antimicrob Agents Chemother* 1995):
- Extended-interval dosing of aminoglycosides (Gentamicin and Tobramycin at 7 mg/kg; Amikacin at 20 mg/kg).
- Log-linear first-order elimination decay interpolation for random serum concentrations drawn 6 to 14 hours post-infusion start.
- Nomogram interval assignment tiers:
  - **q24h:** Concentrations falling below the q24h/q36h boundary.
  - **q36h:** Concentrations falling between the q24h and q36h boundaries.
  - **q48h:** Concentrations falling above the q36h boundary.
  - **Individualized / Traditional PK:** Triggered when CrCl $< 60\text{ mL/min}$ or levels drawn outside the 6–14 h window.
- Amikacin dose-proportional nomogram adaptation (2x scale factor on concentration cutoffs).
- Two-point elimination rate constant ($k_{el}$), half-life ($t_{1/2}$), and expected trough concentration prediction.
- Composite nephrotoxicity risk scoring combining baseline renal function, age, concurrent nephrotoxins (vancomycin), and sepsis.
- Batch CSV cohort processing for clinical pharmacy and antimicrobial stewardship audits.

Requires Python standard library only (zero external runtime dependencies).

---

## Clinical Formulation & Nomogram Boundaries

### Boundary Curve Anchor Points (6–14 Hours Post-Dose)
| Post-Dose Hour | q24h / q36h Boundary (mg/L) | q36h / q48h Boundary (mg/L) | Amikacin q24h / q36h (mg/L) | Amikacin q36h / q48h (mg/L) |
|:--------------:|:---------------------------:|:---------------------------:|:---------------------------:|:---------------------------:|
| 6 h | 11.9 | 17.9 | 23.8 | 35.8 |
| 8 h | 8.1 | 11.6 | 16.2 | 23.2 |
| 10 h | 5.5 | 7.5 | 11.0 | 15.0 |
| 12 h | 3.8 | 4.9 | 7.6 | 9.8 |
| 14 h | 2.6 | 3.2 | 5.2 | 6.4 |

### Pharmacokinetic Equations
$$k_{el} = \frac{\ln(C_1 / C_2)}{t_2 - t_1}, \quad t_{1/2} = \frac{\ln(2)}{k_{el}}$$
$$\text{Predicted Trough} = C_0 \cdot e^{-k_{el} \cdot \tau}$$

---

## Features

- **Standard Hartford Conformance:** Follows Nicolau et al. (1995) validation criteria with CrCl safety boundary guards ($\ge 60\text{ mL/min}$).
- **Amikacin Scaling:** Built-in 2x dose-proportional scale for once-daily 20 mg/kg amikacin regimens.
- **Trough & Accumulation Prediction:** Flags potential accumulation when predicted trough exceeds $2.0\text{ mg/L}$.
- **Batch CSV Processing:** High-throughput clinical validation for hospital pharmacotherapy registries.

---

## Installation & Requirements

- Python 3.10+ (tested on 3.10, 3.11, 3.12)
- Zero external runtime dependencies. `pytest` is optional for running tests.

```bash
git clone https://github.com/abusuraihsakhri/aminoglycoside-hartford-nomogram.git
cd aminoglycoside-hartford-nomogram
```

---

## CLI Usage

### 1. Single Concentration Evaluation (Gentamicin / Tobramycin)
```bash
python cli.py single --level 7.2 --hours 8.0 --crcl 85.0
```

### 2. Single Concentration Evaluation (Amikacin)
```bash
python cli.py single --level 15.0 --hours 8.0 --crcl 85.0 --amikacin
```

### 3. Supervisory Telemetry Audit
```bash
python cli.py audit --task-id TASK-2026-001 --primary 28.5 --secondary 14.2 --json
```

### 4. Batch CSV Cohort Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

---

## Python API Quickstart

```python
from hartford_extended_nomogram import (
    hartford_interval,
    kel_from_two_levels,
    half_life_hours,
    nephrotoxicity_risk,
)

# 1. Determine Hartford Interval
result = hartford_interval(level_mg_l=7.2, hours_post_dose=8.0, crcl_ml_min=85.0)
print(f"Recommended Interval: {result.interval}")
print(f"Rationale: {result.rationale}")

# 2. Evaluate Nephrotoxicity Risk
risk = nephrotoxicity_risk(
    crcl_ml_min=55.0,
    age_years=72,
    on_vancomycin=True,
    therapy_days=8,
    sepsis_or_shock=False,
)
print(f"Nephrotoxicity Risk Tier: {risk['risk_tier']}")
print(f"Monitoring Cadence: {risk['monitoring_cadence']}")
```

---

## Running Tests

Run the test suite using standard `unittest` or `pytest`:

```bash
pytest -v
```

