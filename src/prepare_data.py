import pandas as pd


INPUT_FILE = "data/raw/scenarios.csv"
OUTPUT_FILE = "data/processed/scenarios.csv"


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


def prepare_data():
    df = load_data(INPUT_FILE)

    validate_data(df)

    df = df.drop_duplicates()

    df.to_csv(OUTPUT_FILE, index=False)

    print("Data preparation completed.")
    print(f"Rows: {len(df)}")


if __name__ == "__main__":
    prepare_data()
