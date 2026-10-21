
import sys
from pathlib import Path

import pandas as pd

# Allow imports from the repository's src folder
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from baseline import baseline_controller
from fuzzy_controller import washing_controller

DATA_PATH = ROOT / "data" / "processed" / "scenarios.csv"
OUTPUT_DIR = ROOT / "data" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

required = [
    "scenario_id",
    "dirt_score",
    "load_kg",
    "fabric_type",
    "water_availability_pct",
]
assert all(column in df.columns for column in required)
assert len(df) == 10000
assert not df[required].isnull().any().any()

results = []

for _, row in df.iterrows():
    inputs = (
        row["dirt_score"],
        row["load_kg"],
        row["fabric_type"],
        row["water_availability_pct"],
    )

    baseline = baseline_controller(*inputs)
    fuzzy = washing_controller(*inputs)

    result = {
        "scenario_id": row["scenario_id"],
        "fabric_type": row["fabric_type"],
    }

    for metric in [
        "wash_time_min",
        "water_litre",
        "detergent_ml",
        "spin_rpm",
    ]:
        result[f"baseline_{metric}"] = baseline[metric]
        result[f"fuzzy_{metric}"] = fuzzy[metric]
        result[f"difference_{metric}"] = fuzzy[metric] - baseline[metric]

    results.append(result)

comparison = pd.DataFrame(results)

comparison.to_csv(
    OUTPUT_DIR / "step4_scenario_comparison.csv",
    index=False,
)

metrics = [
    "wash_time_min",
    "water_litre",
    "detergent_ml",
    "spin_rpm",
]

summary = []

for metric in metrics:
    baseline_col = f"baseline_{metric}"
    fuzzy_col = f"fuzzy_{metric}"

    summary.append({
        "metric": metric,
        "baseline_mean": comparison[baseline_col].mean(),
        "fuzzy_mean": comparison[fuzzy_col].mean(),
        "baseline_total": comparison[baseline_col].sum(),
        "fuzzy_total": comparison[fuzzy_col].sum(),
        "mean_difference_fuzzy_minus_baseline": (
            comparison[f"difference_{metric}"].mean()
        ),
    })

summary_df = pd.DataFrame(summary)
summary_df.to_csv(
    OUTPUT_DIR / "step4_summary.csv",
    index=False,
)

print("Scenarios compared:", len(comparison))
print("\nOverall summary:")
print(summary_df.round(2).to_string(index=False))
print("\nFirst five comparisons:")
print(comparison.head().round(2).to_string(index=False))
print("\nSaved comparison CSV and summary CSV in data/reports/")
