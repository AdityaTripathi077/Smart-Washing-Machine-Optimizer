import pandas as pd

file = "data/sample_input.csv"
max_load = 8.0

df = pd.read_csv(file)

errors = []

if df.isnull().any().any():
    errors.append("Missing values found")

if df["scenario_id"].duplicated().any():
    errors.append("Duplicate scenario ID found")

if not df["dirt_score"].between(0, 10).all():
    errors.append("Dirt score must be between 0 and 10")

if not df["load_kg"].between(0.5, max_load).all():
    errors.append("Load must be between 0.5 and 8 kg")

valid_fabrics = ["delicate", "cotton", "synthetic", "heavy"]

if not df["fabric_type"].isin(valid_fabrics).all():
    errors.append("Invalid fabric type found")

if not df["water_availability_pct"].between(0, 100).all():
    errors.append("Water availability must be between 0 and 100")

if errors:
    print("FAIL")
    for error in errors:
        print("-", error)
else:
    print("PASS: All data is valid")
