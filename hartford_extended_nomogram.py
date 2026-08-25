#!/usr/bin/env python3
"""
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
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

Q24_Q36_ANCHORS: List[float] = [11.9, 8.1, 5.5, 3.8, 2.6]
Q36_Q48_ANCHORS: List[float] = [17.9, 11.6, 7.5, 4.9, 3.2]
ANCHOR_HOURS: List[int] = [6, 8, 10, 12, 14]

AMIKACIN_SCALE_FACTOR = 2.0


def _interp_boundary(hour: float, anchors: List[float]) -> float:
    """Log-linear interpolation/extrapolation of a nomogram boundary curve."""
    if hour < ANCHOR_HOURS[0]:
        k = math.log(anchors[0] / anchors[1]) / (ANCHOR_HOURS[1] - ANCHOR_HOURS[0])
        return anchors[0] * math.exp(k * (hour - ANCHOR_HOURS[0]))
    if hour > ANCHOR_HOURS[-1]:
        i = len(anchors) - 2
    else:
        for i in range(len(ANCHOR_HOURS) - 1):
            if ANCHOR_HOURS[i] <= hour <= ANCHOR_HOURS[i + 1]:
                break
    t0, t1 = float(ANCHOR_HOURS[i]), float(ANCHOR_HOURS[i + 1])
    c0, c1 = anchors[i], anchors[i + 1]
    k = math.log(c0 / c1) / (t1 - t0)
    return c0 * math.exp(-k * (hour - t0))


def kel_from_two_levels(c1: float, t1: float, c2: float, t2: float) -> float:
    """First-order elimination rate from two post-dose levels (same dose)."""
    if c1 <= 0 or c2 <= 0 or t2 == t1:
        raise ValueError("need positive concentrations and distinct times")
    return math.log(c1 / c2) / (t2 - t1)


def half_life_hours(kel: float) -> float:
    return round(math.log(2.0) / kel, 3)


@dataclass
class NomogramResult:
    drug: str
    level_mg_l: float
    hours_post_dose: float
    interval: str
    rationale: str


def hartford_interval(level_mg_l: float, hours_post_dose: float,
                      crcl_ml_min: float, amikacin: bool = False) -> NomogramResult:
    """Pick the dosing interval from a single random post-dose level.

    Below the q24h/q36h curve -> continue q24h; between the curves -> extend
    to q36h; above the q36h/q48h curve -> extend to q48h.
    """
    drug = "amikacin" if amikacin else "gentamicin/tobramycin"
    if crcl_ml_min < 60:
        return NomogramResult(drug, level_mg_l, hours_post_dose, "not_applicable",
                              "CrCl < 60 mL/min; use individualized traditional dosing")
    if not 6.0 <= hours_post_dose <= 14.0:
        return NomogramResult(drug, level_mg_l, hours_post_dose, "reassess",
                              "level outside the valid 6-14 h nomogram window")

    scale = AMIKACIN_SCALE_FACTOR if amikacin else 1.0
    b_q24 = _interp_boundary(hours_post_dose, [a * scale for a in Q24_Q36_ANCHORS])
    b_q36 = _interp_boundary(hours_post_dose, [a * scale for a in Q36_Q48_ANCHORS])

    if b_q24 <= level_mg_l < b_q36:
        return NomogramResult(drug, level_mg_l, hours_post_dose, "q36h",
                              f"level {level_mg_l} sits between boundaries "
                              f"{b_q24:.1f} and {b_q36:.1f} at {hours_post_dose} h")
    if level_mg_l >= b_q36:
        return NomogramResult(drug, level_mg_l, hours_post_dose, "q48h",
                              f"level {level_mg_l} above q48h boundary {b_q36:.1f} "
                              f"at {hours_post_dose} h")
    return NomogramResult(drug, level_mg_l, hours_post_dose, "q24h",
                          f"level {level_mg_l} below q24h boundary {b_q24:.1f} "
                          f"at {hours_post_dose} h")


def predict_trough(dose_mg: float, vd_liters: float, kel_per_hr: float,
                   interval_h: float) -> Dict[str, float]:
    """Expected trough just before the next dose and accumulation check."""
    c0 = dose_mg / vd_liters
    trough = c0 * math.exp(-kel_per_hr * interval_h)
    return {
        "predicted_trough_mg_l": round(trough, 3),
        "accumulation_ratio": round(c0 / (c0 * (1 - math.exp(-kel_per_hr * interval_h))), 3),
        "toxic_trough_flag": bool(trough > 2.0),
    }


NEPHROTOX_WEIGHTS = {
    "crcl_lt_30": 3,
    "crcl_30_to_59": 2,
    "age_ge_65": 1,
    "concurrent_vancomycin": 2,
    "therapy_days_ge_7": 1,
    "sepsis_or_shock": 1,
}


def nephrotoxicity_risk(crcl_ml_min: float, age_years: int,
                        on_vancomycin: bool, therapy_days: int,
                        sepsis_or_shock: bool) -> Dict[str, object]:
    """Composite additive score mapped to a monitoring cadence."""
    points = 0
    drivers: List[str] = []
    if crcl_ml_min < 30:
        points += NEPHROTOX_WEIGHTS["crcl_lt_30"]
        drivers.append("CrCl < 30 mL/min")
    elif crcl_ml_min < 60:
        points += NEPHROTOX_WEIGHTS["crcl_30_to_59"]
        drivers.append("CrCl 30-59 mL/min")
    if age_years >= 65:
        points += NEPHROTOX_WEIGHTS["age_ge_65"]
        drivers.append("age >= 65")
    if on_vancomycin:
        points += NEPHROTOX_WEIGHTS["concurrent_vancomycin"]
        drivers.append("concurrent vancomycin")
    if therapy_days >= 7:
        points += NEPHROTOX_WEIGHTS["therapy_days_ge_7"]
        drivers.append("therapy >= 7 days")
    if sepsis_or_shock:
        points += NEPHROTOX_WEIGHTS["sepsis_or_shock"]
        drivers.append("sepsis/shock state")

    if points >= 5:
        tier, cadence = ("high", "daily SCr + daily levels; consider alternative agent")
    elif points >= 3:
        tier, cadence = ("moderate", "SCr every other day; levels every 48-72 h")
    else:
        tier, cadence = ("low", "weekly SCr with standard nomogram re-check")

    return {
        "risk_points": points,
        "risk_tier": tier,
        "drivers": drivers,
        "monitoring_cadence": cadence,
    }


def _demo() -> None:
    cases = [
        {"level": 4.2, "hour": 8.0, "crcl": 95},
        {"level": 9.6, "hour": 10.0, "crcl": 88},
        {"level": 14.5, "hour": 9.0, "crcl": 72},
        {"level": 11.0, "hour": 8.0, "crcl": 45},
        {"level": 19.0, "hour": 8.0, "crcl": 110, "amikacin": True},
    ]
    for case in cases:
        result = hartford_interval(
            case["level"], case["hour"], case["crcl"],
            amikacin=case.get("amikacin", False),
        )
        print({"drug": result.drug, "interval": result.interval,
               "rationale": result.rationale})

    kel = kel_from_two_levels(7.0, 2.0, 2.2, 10.0)
    print({"half_life_h": half_life_hours(kel)})
    print(predict_trough(dose_mg=560, vd_liters=20.0, kel_per_hr=kel, interval_h=36))

    print(nephrotoxicity_risk(crcl_ml_min=52, age_years=71, on_vancomycin=True,
                              therapy_days=9, sepsis_or_shock=True))


if __name__ == "__main__":
    _demo()
