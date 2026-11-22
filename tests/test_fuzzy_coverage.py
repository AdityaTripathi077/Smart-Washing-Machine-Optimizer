"""Rule coverage and limited-water checks for the current fuzzy controller.

Run from the project root:
    python tests/test_fuzzy_coverage.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from fuzzy_controller import washing_controller  # noqa: E402

failures = 0


def check(name, ok, detail=""):
    global failures
    failures += not ok
    print(f"{'OK   ' if ok else 'ERROR'} {name} {detail}")


# 1. The three scenarios that had no recommendation in the Step 3 rule base now get one.
for sid, args in {"SC02-01166": (1.77, 4.25, "synthetic", 100),
                  "SC02-01197": (0.0, 6.62, "cotton", 44),
                  "SC02-06352": (0.0, 6.45, "synthetic", 93)}.items():
    try:
        out = washing_controller(*args)
        check(f"{sid} gets a recommendation", out["wash_time_min"] > 0 and out["detergent_ml"] > 0,
              f"({out['wash_time_min']} min)")
    except ValueError as error:
        check(f"{sid} gets a recommendation", False, str(error))

# 2. Every prepared scenario gets a recommendation, and water never exceeds the supply.
data = pd.read_csv(ROOT / "data" / "processed" / "scenarios.csv")
no_output = over_supply = 0
for r in data.itertuples():
    try:
        out = washing_controller(r.dirt_score, r.load_kg, r.fabric_type, r.water_availability_pct)
    except ValueError:
        no_output += 1
        continue
    over_supply += out["water_litre"] > r.water_availability_pct + 0.01
check(f"all {len(data)} scenarios produce a recommendation", no_output == 0, f"(no output: {no_output})")
check("water never above the supply", over_supply == 0, f"(over supply: {over_supply})")

# 3. Dense grid of valid inputs: no gaps in the rule base.
gaps = 0
for dirt in np.arange(0, 10.01, 0.25):
    for load in np.arange(0.5, 8.01, 0.25):
        for water in range(0, 101, 5):
            try:
                washing_controller(float(dirt), float(load), "cotton", water)
            except ValueError:
                gaps += 1
check("no rule gaps on a dense input grid (26,000+ points)", gaps == 0, f"(gaps: {gaps})")

# 4. Limited water is reported.
low = washing_controller(5, 4.0, "cotton", 10)
check("10% supply: water capped at 10 L and flagged", low["water_litre"] <= 10.01 and low["water_limited"],
      f"({low['water_litre']} L)")
ample = washing_controller(5, 2.0, "cotton", 100)
check("100% supply: not limited", not ample["water_limited"])

# 5. Invalid inputs are still rejected.
for name, args in {"load over 8 kg": (5, 8.5, "cotton", 50), "dirt over 10": (11, 3.0, "cotton", 50),
                   "unknown fabric": (5, 3.0, "wool", 50), "water over 100": (5, 3.0, "cotton", 110)}.items():
    try:
        washing_controller(*args)
        check(f"invalid input rejected: {name}", False)
    except ValueError:
        check(f"invalid input rejected: {name}", True)

print("\nResult:", "all checks behaved as expected" if not failures else f"{failures} check(s) failed")
sys.exit(1 if failures else 0)
