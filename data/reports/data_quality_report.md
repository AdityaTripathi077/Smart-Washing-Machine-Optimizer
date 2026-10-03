# Step 2 Data Quality Report

## Dataset Summary

- Total scenarios: 10,000
- Missing values: 0
- Duplicate scenario IDs: 0
- Valid load range: 0.5–8.0 kg
- Dirt score range: 0–10
- Water availability range: 0–100%

## Data Fields

The dataset contains:
- scenario_id
- dirt_score
- load_kg
- fabric_type
- water_availability_pct

## Validation Status

The generated dataset passed the required validation checks.

- Missing values: PASS
- Duplicate IDs: PASS
- Dirt score range: PASS
- Load range: PASS
- Water availability range: PASS
- Fabric categories: PASS

## Data Source

The 10,000 scenarios are **generated simulation data**, not real-world observations.

The scenarios were generated using a fixed random seed so that the dataset can be reproduced.

## Output

Processed dataset:

`data/processed/scenarios.csv`