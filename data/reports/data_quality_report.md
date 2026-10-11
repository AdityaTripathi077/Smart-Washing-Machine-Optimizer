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

## Fabric Distribution

| Fabric Type | Count | Percentage |
|---|---:|---:|
| delicate | 2513 | 25.1% |
| synthetic | 2511 | 25.1% |
| heavy | 2508 | 25.1% |
| cotton | 2468 | 24.7% |
| Total | 10000 | 100% |

The four fabric categories are reasonably balanced in the generated simulation data.
## Scenario Categories

The 10,000 valid generated scenarios are categorized using the following rules.

### Normal Scenarios

Valid scenarios that do not meet the boundary or stress conditions.

### Boundary Scenarios

A scenario is classified as a boundary case if any input is near an allowed limit:

- dirt_score <= 1 or dirt_score >= 9
- load_kg <= 0.75 or load_kg >= 7.75
- water_availability_pct <= 5 or water_availability_pct >= 95

### Stress Scenarios

A valid scenario is classified as a stress case if any of these conditions apply:

- dirt_score >= 8
- load_kg >= 6 kg
- water_availability_pct <= 25%

Boundary cases take priority when a scenario meets both boundary and stress conditions.

### Invalid Scenarios

Invalid scenarios are tested separately and are not included in the 10,000 valid generated scenarios. The invalid test data includes values outside the allowed ranges, such as dirt_score = 11, load_kg = 9 kg, an unknown fabric type, and water_availability_pct = 110%.

### Category Counts

The exact counts for normal, boundary, and stress scenarios must be calculated from the generated dataset using the rules above. They should not be estimated.

The generated dataset contains 10,000 valid scenarios. Invalid test cases are documented separately.
