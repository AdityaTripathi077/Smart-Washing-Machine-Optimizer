import pandas as pd


INPUT_FILE = "data/raw/scenarios.csv"
OUTPUT_FILE = "data/processed/scenarios.csv"
REJECTED_FILE = "data/processed/rejected_scenarios.csv"   # invalid rows are kept here, never dropped silently


def load_data(file_path):
    return pd.read_csv(file_path)


def validate_data(df):
    required_columns = [
        "scenario_id",
        "dirt_score",
        "load_kg",
        "fabric_type",
        "water_availability_pct"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing column: {column}")

    if df["scenario_id"].duplicated().any():
        raise ValueError("Duplicate scenario_id found")

    if not df["dirt_score"].between(0, 10).all():
        raise ValueError("Invalid dirt_score")

    if not df["load_kg"].between(0.5, 8.0).all():
        raise ValueError("Invalid load_kg")

    if not df["water_availability_pct"].between(0, 100).all():
        raise ValueError("Invalid water_availability_pct")

    valid_fabrics = ["delicate", "cotton", "synthetic", "heavy"]

    if not df["fabric_type"].isin(valid_fabrics).all():
        raise ValueError("Invalid fabric_type")

    return True


def split_valid_invalid(df):
    """Return (valid_rows, invalid_rows). A row is invalid if any input is out of range."""
    fabrics = ["delicate", "cotton", "synthetic", "heavy"]
    ok = (
        df["dirt_score"].between(0, 10)
        & df["load_kg"].between(0.5, 8.0)
        & df["water_availability_pct"].between(0, 100)
        & df["fabric_type"].isin(fabrics)
    )
    return df[ok], df[~ok]


def prepare_data():
    df = load_data(INPUT_FILE)

    # Structure checks (missing columns, duplicate IDs) still stop the run.
    required = ["scenario_id", "dirt_score", "load_kg", "fabric_type", "water_availability_pct"]
    for column in required:
        if column not in df.columns:
            raise ValueError(f"Missing column: {column}")
    if df["scenario_id"].duplicated().any():
        raise ValueError("Duplicate scenario_id found")

    valid, invalid = split_valid_invalid(df.drop_duplicates())

    valid.to_csv(OUTPUT_FILE, index=False)
    invalid.to_csv(REJECTED_FILE, index=False)   # header-only file when nothing was rejected

    print("Data preparation completed.")
    print(f"Valid rows kept: {len(valid)}")
    print(f"Invalid rows kept separately in {REJECTED_FILE}: {len(invalid)}")
    # data/invalid_input.csv (the hand-written test row) is never touched by this script.


if __name__ == "__main__":
    prepare_data()
