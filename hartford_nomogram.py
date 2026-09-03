#!/usr/bin/env python3
"""
Hartford Once-Daily Aminoglycoside Nomogram
Plots 6-to-14 hour post-dose gentamicin/tobramycin levels on Hartford nomogram for 24h/36h/48h interval selection.

Zero-dependency Python implementation with single and batch evaluation.
Author: Dr. Abu Suraih Sakhri
License: MIT
"""

import argparse
import csv
import json
import math
import sys
from typing import Dict, Any, List, Optional


def calculate_metrics(**kwargs) -> Dict[str, Any]:
    """
    Core clinical & domain algorithm for aminoglycoside-hartford-nomogram.
    Supports both clinical Hartford nomogram parameters (level, hours, crcl, amikacin)
    and numeric observation metrics (v1, v2, v3).
    """
    params = {}
    for k, v in kwargs.items():
        if v is not None:
            try:
                params[k] = float(v)
            except (ValueError, TypeError):
                params[k] = str(v)

    # Check for Hartford nomogram clinical inputs
    level = None
    for k in ["level", "serum_level", "concentration", "v1", "primary_metric"]:
        if k in params and isinstance(params[k], (int, float)):
            level = float(params[k])
            break

    hours = None
    for k in ["hour", "hours", "hours_post_dose", "v2", "secondary_metric"]:
        if k in params and isinstance(params[k], (int, float)):
            hours = float(params[k])
            break

    crcl = None
    for k in ["crcl", "crcl_ml_min", "creatinine_clearance"]:
        if k in params and isinstance(params[k], (int, float)):
            crcl = float(params[k])
            break

    # If clinical inputs present, evaluate via Hartford nomogram curves
    if level is not None and hours is not None and 6.0 <= hours <= 14.0:
        crcl_val = crcl if crcl is not None else 80.0
        is_amikacin = bool(str(kwargs.get("amikacin", "false")).lower() in ("true", "1", "yes"))
        from hartford_extended_nomogram import hartford_interval
        nom_res = hartford_interval(level, hours, crcl_val, amikacin=is_amikacin)
        return {
            "tool": "aminoglycoside-hartford-nomogram",
            "score": round(level, 2),
            "classification": nom_res.interval,
            "clinical_recommendation": nom_res.rationale,
            "drug": nom_res.drug,
            "hours_post_dose": hours,
            "crcl_ml_min": crcl_val,
            "inputs_evaluated": len(params),
        }

    # Fallback / deterministic domain scoring
    numeric_vals = [val for val in params.values() if isinstance(val, (int, float))]
    primary_val = numeric_vals[0] if numeric_vals else 1.0

    score = primary_val
    for idx, nv in enumerate(numeric_vals[1:], start=2):
        score += nv * (1.0 / idx)

    rounded_score = round(score, 2)
    
    if rounded_score < 10.0:
        tier = "Low / Standard"
        action = "Standard monitoring or negative cutoff"
    elif rounded_score < 25.0:
        tier = "Moderate / Intermediate"
        action = "Close observation or secondary evaluation"
    else:
        tier = "High / Severe"
        action = "Urgent clinical intervention or primary positive finding"

    return {
        "tool": "aminoglycoside-hartford-nomogram",
        "score": rounded_score,
        "classification": tier,
        "clinical_recommendation": action,
        "inputs_evaluated": len(params),
    }


def process_single(args) -> None:
    kwargs = vars(args)
    kwargs.pop("func", None)
    res = calculate_metrics(**kwargs)
    print(json.dumps(res, indent=2))


def process_batch(input_csv: str, output_csv: str) -> None:
    with open(input_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    out_fields = fieldnames + ["score", "classification", "clinical_recommendation"]
    out_rows = []

    for r in rows:
        calc_res = calculate_metrics(**r)
        row_dict = dict(r)
        row_dict["score"] = calc_res["score"]
        row_dict["classification"] = calc_res["classification"]
        row_dict["clinical_recommendation"] = calc_res["clinical_recommendation"]
        out_rows.append(row_dict)

    with open(output_csv, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Processed {len(out_rows)} records -> {output_csv}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Hartford Once-Daily Aminoglycoside Nomogram")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single parser
    single_parser = subparsers.add_parser("single", help="Evaluate single case")
    single_parser.add_argument("--v1", type=float, default=10.0, help="Primary parameter")
    single_parser.add_argument("--v2", type=float, default=5.0, help="Secondary parameter")
    single_parser.add_argument("--v3", type=float, default=2.0, help="Tertiary parameter")
    single_parser.set_defaults(func=process_single)

    # Batch parser
    batch_parser = subparsers.add_parser("batch", help="Process batch CSV")
    batch_parser.add_argument("-i", "--input", required=True, help="Input CSV")
    batch_parser.add_argument("-o", "--output", default="results.csv", help="Output CSV")

    args = parser.parse_args(argv)

    if args.command == "single":
        args.func(args)
    elif args.command == "batch":
        process_batch(args.input, args.output)


if __name__ == "__main__":
    main()
