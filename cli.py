#!/usr/bin/env python3
"""
Command Line Interface for Aminoglycoside Hartford Nomogram.
Zero external runtime dependencies.
"""
import argparse
import csv
import json
import sys
from typing import Optional, List

from hartford_nomogram import calculate_metrics, process_batch


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="aminoglycoside-hartford-nomogram",
        description="Hartford Once-Daily Aminoglycoside Nomogram (Gentamicin, Tobramycin, Amikacin)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # single / calc
    p_single = subparsers.add_parser("single", help="Evaluate single aminoglycoside concentration")
    p_single.add_argument("--level", "-l", type=float, default=7.5, help="Serum concentration (mg/L)")
    p_single.add_argument("--hours", "-t", type=float, default=8.0, help="Hours post-infusion start (6-14 h)")
    p_single.add_argument("--crcl", type=float, default=85.0, help="Creatinine clearance (mL/min)")
    p_single.add_argument("--amikacin", action="store_true", help="Amikacin evaluation (scaled cutoffs)")
    p_single.add_argument("--v1", type=float, help="Fallback primary metric")
    p_single.add_argument("--v2", type=float, help="Fallback secondary metric")
    p_single.add_argument("--json", action="store_true", help="Output as JSON")

    # audit
    p_audit = subparsers.add_parser("audit", help="Run single task supervisory telemetry evaluation")
    p_audit.add_argument("--task-id", default="TASK-2026-001")
    p_audit.add_argument("--target", default="KEY-TARGET-01")
    p_audit.add_argument("--primary", type=float, default=28.5)
    p_audit.add_argument("--secondary", type=float, default=14.2)
    p_audit.add_argument("--critical", action="store_true")
    p_audit.add_argument("--status", default="DISCORDANT")
    p_audit.add_argument("--json", action="store_true", help="Output as JSON")

    # batch
    p_batch = subparsers.add_parser("batch", help="Batch process CSV records")
    p_batch.add_argument("-i", "--input", required=True, help="Input CSV path")
    p_batch.add_argument("-o", "--output", default="results.csv", help="Output CSV path")

    args = parser.parse_args(argv)

    if args.command == "single":
        kwargs = {
            "level": args.level if args.v1 is None else args.v1,
            "hours": args.hours if args.v2 is None else args.v2,
            "crcl": args.crcl,
            "amikacin": args.amikacin,
        }
        res = calculate_metrics(**kwargs)
        if args.json or True:
            print(json.dumps(res, indent=2))
        return 0

    if args.command == "audit":
        audit_res = {
            "task_id": args.task_id,
            "target_identifier": args.target,
            "primary_metric": args.primary,
            "secondary_metric": args.secondary,
            "status_descriptor": args.status,
            "is_critical_flag": args.critical,
            "overall_status": "CRITICAL_INTERVENTION_REQUIRED" if args.primary > 25.0 and args.critical else ("ELEVATED_RISK_WARNING" if args.primary > 25.0 or args.critical else "NOMINAL"),
            "clinical_standard": "Hartford Extended-Interval Nomogram (Nicolau et al. 1995)",
        }
        if args.json:
            print(json.dumps(audit_res, indent=2))
        else:
            print(f"Audit Task: {audit_res['task_id']} | Status: [{audit_res['overall_status']}]")
        return 0

    if args.command == "batch":
        process_batch(args.input, args.output)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())

