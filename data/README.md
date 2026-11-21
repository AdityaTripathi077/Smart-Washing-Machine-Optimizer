# Data Description

This folder contains the data used for the Smart Washing Machine Optimizer.

## Input Fields

| Field | Meaning | Type / Unit | Allowed Range |
|---|---|---|---|
| scenario_id | Unique name for each washing case | Text | SC02-001, SC02-002... |
| dirt_score | How dirty the clothes are | Number | 0 to 10 |
| load_kg | Weight of clothes | kg | 0.5 to machine capacity |
| fabric_type | Type of fabric | Category | delicate, cotton, synthetic, heavy |
| water_availability_pct | Water available for washing | Percentage | 0 to 100 |

## Output Fields

| Field | Meaning | Unit |
|---|---|---|
| wash_time_min | Recommended washing time | minutes |
| water_litre | Recommended water usage | litres |
| detergent_ml | Recommended detergent amount | ml |
| spin_rpm | Recommended spin speed | RPM |

## Data Rules

- dirt_score must be between 0 and 10
- load_kg must not exceed the selected machine capacity
- water_availability_pct must be between 0 and 100
- fabric_type must use the documented categories
- scenario_id must be unique
- Required fields cannot be empty
- Numeric values should not contain units inside the CSV

## Starter Data

Step 1 uses a small sample dataset.

## Machine Capacity Source

For this project, we use an 8 kg washing machine capacity.

Machine: LG T80VBSF1Z  
Maximum wash capacity: 8.0 kg

Source: LG India  
https://www.lg.com/in/laundry/top-loading-washing-machines/t80vbsf1z/

## Simulation Assumptions

The following fields are team-defined inputs for simulation:

- dirt_score: 0–10
- water_availability_pct: 0–100
- fabric_type: delicate, cotton, synthetic, heavy

These are simulation variables and are not claimed to be direct manufacturer sensor measurements.

## Sources and Assumptions

The machine capacity source is documented above.

The dirt_score, water_availability_pct, and fabric_type ranges are team-defined simulation assumptions.

Any simulated or assumed values will be clearly marked.

A larger dataset of 10,000+ scenarios is generated in Step 2 using reproducible simulation.
## Data Generation Process

The Step 2 dataset is generated using Python with a fixed random seed.
The generator creates 10,000 valid washing scenarios using the documented input ranges.

### How to regenerate (command and seed)

```text
python src/generate_scenarios.py   # seed 42 (random.seed(42) in the script); writes data/raw/scenarios.csv
python src/prepare_data.py         # writes data/processed/scenarios.csv
```

The seed is fixed in `src/generate_scenarios.py`, so every run produces the same 10,000 rows.

### Invalid scenarios are kept separately

Invalid inputs are never mixed into the valid dataset:
- `data/invalid_input.csv` holds the hand-written invalid test rows: INVALID-001 (every input out of range) and SC02-005 (8.5 kg load, over the 8 kg machine capacity; mandatory test case 5). SC02-005 was moved here from the sample so `data/sample_input.csv` contains only valid rows. The generator and `prepare_data.py` never overwrite it.
- If any generated row is out of range, `prepare_data.py` moves it to `data/processed/rejected_scenarios.csv` instead of dropping it silently. The current file is empty (header only) because all 10,000 generated rows are valid.
- Reproduce the invalid check with `python src/validate_data.py data/invalid_input.csv` (expected result: FAIL).
