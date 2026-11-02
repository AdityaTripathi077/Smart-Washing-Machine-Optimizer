"""Guards against the fuzzy module and the accepted Step 3 report drifting apart.

The seven values below are copied from data/reports/step3_baseline_vs_fuzzy.md.
Run from the project root:
    python tests/test_fuzzy_matches_report.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from fuzzy_controller import washing_controller  # noqa: E402

# (dirt, load, fabric, water%) -> (time, water, detergent, rpm) from the Step 3 report
EXPECTED = [
    ((2, 2.0, "cotton", 100), (45.76, 60.00, 46.95, 1235)),
    ((5, 4.0, "synthetic", 60), (52.50, 59.89, 55.00, 900)),
    ((9, 7.0, "heavy", 100), (65.63, 86.06, 70.72, 1235)),
    ((5, 2.0, "delicate", 80), (52.50, 56.88, 55.00, 565)),
    ((7, 5.0, "cotton", 20), (55.43, 53.95, 58.49, 1235)),
    ((0, 0.5, "delicate", 0), (27.33, 33.17, 24.83, 565)),
    ((10, 8.0, "heavy", 100), (77.67, 86.83, 85.17, 1235)),
]


def main():
    bad = 0
    for args, expected in EXPECTED:
        out = washing_controller(*args)
        got = (out["wash_time_min"], out["water_litre"], out["detergent_ml"], out["spin_rpm"])
        ok = all(abs(g - e) <= 0.02 for g, e in zip(got, expected))
        bad += not ok
        print(f"{'OK   ' if ok else 'ERROR'} {args}: got {got}, report says {expected}")
    print(f"\nResult: {len(EXPECTED) - bad}/{len(EXPECTED)} match the Step 3 report")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
