# Step 2 Data Quality Report

## Dataset Summary

- Total scenarios: 10,000
- Missing values: 0
- Duplicate scenario IDs: 0
- Valid load range: 0.5–8.0 kg
- Dirt score range: 0–10
- Water availability range: 0–100%

## Data Fields

The dataset contains the following input fields:

- `scenario_id`
- `dirt_score`
- `load_kg`
- `fabric_type`
- `water_availability_pct`

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

The scenarios were generated using Python with a fixed random seed so that the dataset can be reproduced.

## Output

Processed dataset:

`data/processed/scenarios.csv`

Raw dataset:

`data/raw/scenarios.csv`

## Fabric Distribution

| Fabric Type | Count | Percentage |
|---|---:|---:|
| delicate | 2513 | 25.13% |
| synthetic | 2511 | 25.11% |
| heavy | 2508 | 25.08% |
| cotton | 2468 | 24.68% |
| **Total** | **10000** | **100%** |

The four fabric categories are reasonably balanced in the generated simulation data.

## Scenario Categories

The 10,000 valid generated scenarios are categorized using the documented rules below.

### Normal Scenarios

A scenario is classified as normal if it is valid and does not meet either the boundary or stress conditions.

### Boundary Scenarios

A scenario is classified as a boundary case if any input meets one of these conditions:

- `dirt_score` <= 1 or `dirt_score` >= 9
- `load_kg` <= 0.75 or `load_kg` >= 7.75
- `water_availability_pct` <= 5 or `water_availability_pct` >= 95

### Stress Scenarios

A valid scenario is classified as a stress case if any of these conditions apply:

- `dirt_score` >= 8
- `load_kg` >= 6 kg
- `water_availability_pct` <= 25%

Boundary cases take priority when a scenario meets both boundary and stress conditions.

### Category Counts

The following counts were calculated from the generated dataset using Python and the documented categorization rules.

| Category | Count | Percentage |
|---|---:|---:|
| Normal | 3274 | 32.74% |
| Boundary | 3461 | 34.61% |
| Stress | 3265 | 32.65% |
| **Total valid scenarios** | **10000** | **100%** |

## Invalid Scenario Testing

Invalid scenarios are tested separately and are not included in the 10,000 valid generated scenarios.

The invalid test data includes:

| Field | Invalid Value | Reason |
|---|---|---|
| `dirt_score` | 11 | Exceeds the allowed range of 0–10 |
| `load_kg` | 9 kg | Exceeds the machine capacity of 8 kg |
| `fabric_type` | unknown | Not an allowed fabric category |
| `water_availability_pct` | 110 | Exceeds the allowed range of 0–100 |

These values are used to check that invalid input is detected by the validation process.

## Reproducibility

The scenario generator uses a fixed random seed. Running the generator with the same code, seed, and settings reproduces the same input scenarios.

The category counts are calculated from the generated dataset using the rules documented in this report.
