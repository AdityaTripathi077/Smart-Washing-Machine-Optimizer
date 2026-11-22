"""Write the reference result for the Step 6 UI-versus-code check (T09).

It calls the saved baseline and fuzzy controller DIRECTLY (not through the app) for the
"Normal wash" example and saves one CSV row. Compare it with the CSV downloaded from the app.

Run from the project root:
    python src/check_product_prediction.py
"""
import csv
from pathlib import Path

from baseline import baseline_controller
from fuzzy_controller import washing_controller

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "reports" / "step5_ui_reference_prediction.csv"

INPUT = {"dirt_score": 5.0, "load_kg": 4.0, "fabric_type": "cotton", "water_availability_pct": 100.0}
OUTPUTS = ["wash_time_min", "water_litre", "detergent_ml", "spin_rpm"]


def main():
    args = (INPUT["dirt_score"], INPUT["load_kg"], INPUT["fabric_type"], INPUT["water_availability_pct"])
    base, fuzzy = baseline_controller(*args), washing_controller(*args)
    supply = INPUT["water_availability_pct"] / 100 * 100.0
    row = dict(INPUT)
    row.update({f"baseline_{k}": base[k] for k in OUTPUTS})
    row.update({f"fuzzy_{k}": fuzzy[k] for k in OUTPUTS})
    row["water_supply_litre"] = round(supply, 2)
    row["fuzzy_water_limited"] = bool(fuzzy.get("water_limited", False))
    row["baseline_water_over_supply"] = base["water_litre"] > supply + 0.01
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)
    print("Reference input:", INPUT)
    print("Fuzzy:", {k: fuzzy[k] for k in OUTPUTS})
    print("Saved:", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
