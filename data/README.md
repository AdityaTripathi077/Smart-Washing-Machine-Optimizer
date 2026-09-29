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

A larger dataset of 10,000+ scenarios will be created in a later step.

## Sources and Assumptions

The team will document the sources used for machine capacity and input ranges.

Any simulated or assumed values will be clearly marked.
