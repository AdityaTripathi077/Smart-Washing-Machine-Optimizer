"""Compare the reference CSV with the CSV downloaded from the running app (Step 6, T09).

Steps:
1. python src/check_product_prediction.py          (writes the reference CSV)
2. In the app click "Normal wash", then "Recommend settings", then "Download this result as CSV".
3. Save the download as data/reports/step6_ui_prediction.csv
4. python src/compare_step6_predictions.py

Prints PASS if every input and output matches, otherwise FAIL and the differing columns.
"""
import argparse
import csv
from math import isclose
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "data" / "reports"
TEXT_FIELDS = ["fabric_type", "fuzzy_water_limited", "baseline_water_over_supply"]
NUMBER_FIELDS = ["dirt_score", "load_kg", "water_availability_pct", "water_supply_litre"] + [
    f"{tag}_{k}" for tag in ("baseline", "fuzzy") for k in ("wash_time_min", "water_litre", "detergent_ml", "spin_rpm")]


def read_row(path):
    with path.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != 1:
        raise ValueError(f"{path.name}: expected exactly one result row.")
    row = rows[0]
    for field in TEXT_FIELDS + NUMBER_FIELDS:
        if row.get(field) in (None, ""):
            raise ValueError(f"{path.name}: missing value for {field}.")
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path, nargs="?", default=REPORT_DIR / "step5_ui_reference_prediction.csv")
    parser.add_argument("app_download", type=Path, nargs="?", default=REPORT_DIR / "step6_ui_prediction.csv")
    args = parser.parse_args()
    try:
        ref, app = read_row(args.reference), read_row(args.app_download)
        differences = [f for f in NUMBER_FIELDS if not isclose(float(ref[f]), float(app[f]), abs_tol=0.005)]
        differences += [f for f in TEXT_FIELDS if ref[f].strip().lower() != app[f].strip().lower()]
    except (OSError, ValueError, csv.Error) as error:
        parser.exit(1, f"FAIL: {error}\n")
    if differences:
        parser.exit(1, f"FAIL: Different values in {', '.join(differences)}.\n")
    print("PASS: all inputs, baseline outputs and fuzzy outputs match.")
    print(f"Fuzzy water {app['fuzzy_water_litre']} L, wash time {app['fuzzy_wash_time_min']} min.")


if __name__ == "__main__":
    main()
