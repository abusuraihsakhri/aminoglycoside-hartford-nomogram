import json
import os
import pytest
from hartford_nomogram import calculate_metrics, process_batch
from cli import main


def test_hartford_nomogram_single():
    res = calculate_metrics(v1=12.0, v2=4.0)
    assert "score" in res
    assert "classification" in res
    assert res["score"] > 0


def test_hartford_nomogram_clinical_interval():
    # Level 7.0 at 8 hours -> q24h
    res_q24 = calculate_metrics(level=7.0, hours=8.0, crcl=90.0)
    assert res_q24["classification"] == "q24h"

    # Level 9.5 at 8 hours -> between 8.1 and 11.6 -> q36h
    res_q36 = calculate_metrics(level=9.5, hours=8.0, crcl=90.0)
    assert res_q36["classification"] == "q36h"

    # Level 14.0 at 8 hours -> above 11.6 -> q48h
    res_q48 = calculate_metrics(level=14.0, hours=8.0, crcl=90.0)
    assert res_q48["classification"] == "q48h"


def test_hartford_nomogram_batch(tmp_path):
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("Patient,v1,v2\nPat_001,15.0,3.0\nPat_002,5.0,1.0\n", encoding="utf-8")
    
    process_batch(str(csv_in), str(csv_out))
    assert csv_out.exists()
    content = csv_out.read_text(encoding="utf-8")
    assert "Pat_001" in content
    assert "score" in content


def test_cli_audit_and_batch(tmp_path):
    assert main(["single", "--level", "6.5", "--hours", "7.0"]) == 0
    assert main(["audit", "--json", "--primary", "27.0"]) == 0

    sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample.csv")
    out_csv = tmp_path / "out_sample.csv"
    assert main(["batch", "-i", sample_path, "-o", str(out_csv)]) == 0
    assert out_csv.exists()

