"""Tests for the fuzzy controller.

Run from the project root:
    python tests/test_fuzzy_matches_report.py

Part A: with the ORIGINAL Step 3 settings (complete_rules=False, limit_water=False) the
        controller must still reproduce the 7 values in data/reports/step3_baseline_vs_fuzzy.md.
Part B: the Step 4 revision (default settings) must
        - give an output for the 3 scenarios that had none (SC02-01166, SC02-01197, SC02-06352),
        - give an output everywhere on a grid of valid inputs (no rule gaps),
        - never recommend more water than the assumed supply,
        - reject invalid inputs,
        - match the regression values below (the 4 unchanged cases equal the Step 3 report;
          3 cases change on purpose: see the comments).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from fuzzy_controller import AVAILABLE_WATER_AT_100_PCT, washing_controller  # noqa: E402

KEYS = ("wash_time_min", "water_litre", "detergent_ml", "spin_rpm")

# (dirt, load, fabric, water%) -> (time, water, detergent, rpm) from the Step 3 report
STEP3_REPORT = [
    ((2, 2.0, "cotton", 100), (45.76, 60.00, 46.95, 1235)),
    ((5, 4.0, "synthetic", 60), (52.50, 59.89, 55.00, 900)),
    ((9, 7.0, "heavy", 100), (65.63, 86.06, 70.72, 1235)),
    ((5, 2.0, "delicate", 80), (52.50, 56.88, 55.00, 565)),
    ((7, 5.0, "cotton", 20), (55.43, 53.95, 58.49, 1235)),
    ((0, 0.5, "delicate", 0), (27.33, 33.17, 24.83, 565)),
    ((10, 8.0, "heavy", 100), (77.67, 86.83, 85.17, 1235)),
]

# Same 7 inputs with the Step 4 revision. Water differs from the report in 3 cases:
#   (9, 7.0, heavy, 100)   new rule 13 (high availability + medium load -> medium water)
#   (7, 5.0, cotton, 20)   water capped at the 20 L supply
#   (0, 0.5, delicate, 0)  water capped at the 0 L supply (no water available)
REVISED = [
    ((2, 2.0, "cotton", 100), (45.76, 60.00, 46.95, 1235)),
    ((5, 4.0, "synthetic", 60), (52.50, 59.89, 55.00, 900)),
    ((9, 7.0, "heavy", 100), (65.63, 71.30, 70.72, 1235)),
    ((5, 2.0, "delicate", 80), (52.50, 56.88, 55.00, 565)),
    ((7, 5.0, "cotton", 20), (55.43, 20.00, 58.49, 1235)),
    ((0, 0.5, "delicate", 0), (27.33, 0.00, 24.83, 565)),
    ((10, 8.0, "heavy", 100), (77.67, 86.83, 85.17, 1235)),
]

# The 3 valid scenarios that had no output before the revision
FORMER_FAILURES = [
    (1.77, 4.25, "synthetic", 100),   # SC02-01166
    (0.0, 6.62, "cotton", 44),        # SC02-01197
    (0.0, 6.45, "synthetic", 93),     # SC02-06352
]

failures = 0


def check(name, ok, detail=""):
    global failures
    failures += not ok
    print(f"{'OK   ' if ok else 'ERROR'} {name} {detail}")


def values(out):
    return tuple(out[k] for k in KEYS)


def close(got, expected):
    return all(abs(g - e) <= 0.02 for g, e in zip(got, expected))


print("PART A: original Step 3 settings reproduce the Step 3 report")
for args, expected in STEP3_REPORT:
    got = values(washing_controller(*args, complete_rules=False, limit_water=False))
    check(str(args), close(got, expected), f"got {got}")

print("\nPART B: Step 4 revision")
for args, expected in REVISED:
    got = values(washing_controller(*args))
    check(f"regression {args}", close(got, expected), f"got {got}")

for args in FORMER_FAILURES:
    try:
        out = washing_controller(*args)
        check(f"former no-output case {args}", all(np.isfinite(v) for v in values(out)), str(values(out)))
    except ValueError as error:
        check(f"former no-output case {args}", False, str(error))

empty, over, n = [], [], 0
for fabric in ("delicate", "cotton", "synthetic", "heavy"):
    for dirt in np.arange(0, 10.01, 0.5):
        for load in np.arange(0.5, 8.01, 0.25):
            for water in range(0, 101, 5):
                n += 1
                args = (round(float(dirt), 2), round(float(load), 2), fabric, water)
                try:
                    out = washing_controller(*args)
                except ValueError:
                    empty.append(args)
                    continue
                if out["water_litre"] > water * AVAILABLE_WATER_AT_100_PCT / 100 + 1e-9:
                    over.append(args)
check(f"no rule gaps on a grid of {n} valid inputs", not empty, f"{len(empty)} without output")
check(f"water never above the supply on the same grid", not over, f"{len(over)} above supply")

low = washing_controller(5, 5.0, "cotton", 10)
check("low water (10%) is capped at 10 L and flagged", low["water_litre"] <= 10.0 and low["water_limited"], str(low))
none = washing_controller(5, 5.0, "cotton", 0)
check("0% water gives 0 L and is flagged", none["water_litre"] == 0.0 and none["water_limited"], str(none))
full = washing_controller(2, 2.0, "cotton", 100)
check("plenty of water is not flagged", not full["water_limited"], str(full))

for bad in [(11, 4, "cotton", 50), (5, 9, "cotton", 50), (5, 4, "unknown", 50), (5, 4, "cotton", 110)]:
    try:
        washing_controller(*bad)
        check(f"invalid input rejected {bad}", False)
    except ValueError:
        check(f"invalid input rejected {bad}", True)

print(f"\nResult: {'ALL TESTS PASSED' if not failures else str(failures) + ' TEST(S) FAILED'}")
sys.exit(1 if failures else 0)
