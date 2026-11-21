"""Validate a washing-scenario CSV against the Step 1 input rules.

Run from the project root:
    python src/validate_data.py                          # data/sample_input.csv  -> PASS
    python src/validate_data.py data/invalid_input.csv   # invalid test row      -> FAIL (exit code 1)
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILE = ROOT / "data" / "sample_input.csv"
MAX_LOAD = 8.0
VALID_FABRICS = ["delicate", "cotton", "synthetic", "heavy"]
REQUIRED = ["scenario_id", "dirt_score", "load_kg", "fabric_type", "water_availability_pct"]


def validate(df):
    """Return a list of error messages (empty list = valid)."""
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        return [f"Missing columns: {', '.join(missing)}"]

    errors = []
    if df[REQUIRED].isnull().any().any():
        errors.append("Missing values found")
    if df["scenario_id"].duplicated().any():
        errors.append("Duplicate scenario ID found")
    if not pd.to_numeric(df["dirt_score"], errors="coerce").between(0, 10).all():
        errors.append("Dirt score must be between 0 and 10")
    if not pd.to_numeric(df["load_kg"], errors="coerce").between(0.5, MAX_LOAD).all():
        errors.append("Load must be between 0.5 and 8 kg")
    if not df["fabric_type"].isin(VALID_FABRICS).all():
        errors.append("Invalid fabric type found")
    if not pd.to_numeric(df["water_availability_pct"], errors="coerce").between(0, 100).all():
        errors.append("Water availability must be between 0 and 100")
    return errors


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FILE
    errors = validate(pd.read_csv(path))
    print(f"Checked: {path}")
    if errors:
        print("FAIL")
        for error in errors:
            print("-", error)
        sys.exit(1)
    print("PASS: All data is valid")


if __name__ == "__main__":
    main()
