
# Step 4 - Fair Baseline Comparison

## Team and Project
- Project: Smart Washing Machine Optimizer
- Team: Smart Spin
- Step 4 branch: step-4-baseline

## Question
Does the initial Mamdani fuzzy controller produce different washing recommendations from the fixed-preset baseline when both methods receive the same 10,000 valid scenarios?

## Data and Scenarios
The comparison will use the prepared synthetic dataset at `data/processed/scenarios.csv`.
The dataset contains 10,000 generated scenarios with a fixed random seed.
The same valid input scenarios will be evaluated by both methods.

## Baseline Rule
The baseline selects fixed washing settings according to fabric type:
- Delicate: 30 minutes, 40 litres, 30 ml detergent, 600 RPM
- Cotton: 45 minutes, 60 litres, 50 ml detergent, 1000 RPM
- Synthetic: 35 minutes, 50 litres, 40 ml detergent, 800 RPM
- Heavy: 60 minutes, 75 litres, 60 ml detergent, 1200 RPM

These are team-defined reference presets, not manufacturer recommendations.

## Measures
Compare both methods using:
- Wash time (minutes)
- Water usage (litres)
- Detergent amount (ml)
- Spin speed (RPM)

Report mean and total values where appropriate, and break down results by normal, boundary, and stress scenarios.

Energy savings will not be claimed unless a defensible energy measure is defined.

## Fair-Comparison Checks
- Both methods receive the same input scenarios.
- Both methods use the same valid dataset rows.
- Invalid inputs are excluded from valid-scenario performance summaries and tested separately.
- Step 3 code, notebook, and reports remain unchanged.

## Results
Results will be added after the comparison script runs successfully.
No improvement is claimed before evaluating the actual results.
The baseline and fuzzy controller were evaluated on the same 10,000 synthetic scenarios.

| Metric | Baseline Mean | Fuzzy Mean | Mean Difference |
|---|---:|---:|---:|
| Wash time (min) | 42.48 | 55.88 | +13.40 |
| Water usage (litres) | 56.22 | 60.00 | +3.77 |
| Detergent (ml) | 44.97 | 51.04 | +6.07 |
| Spin speed (RPM) | 899.42 | 918.55 | +19.13 |

The fuzzy controller produced higher average wash time, water usage, detergent usage, and spin speed than the fixed-preset baseline. Therefore, these results do not demonstrate resource savings.

## Interpretation

The current fuzzy controller takes approximately 13.40 additional minutes per scenario on average, uses 3.77 additional litres of water, and uses 6.07 additional ml of detergent compared with the baseline.

These differences indicate that the current rules and membership functions require further tuning. Higher spin speed alone does not demonstrate better cleaning performance.

## Limitations

- The dataset contains synthetic scenarios and does not establish real-world washing performance.
- The baseline uses fixed settings based on fabric type.
- The fuzzy controller uses preliminary rules and temporary fallback behaviour when no output membership is activated.
- Cleaning quality was not measured against an independent target.
- Energy consumption was not modelled; no energy-saving claim is made.
- Results should be reproduced after the fuzzy rules are improved.

## Next Tuning Priorities

1. Review wash-time rules and membership functions.
2. Review water-use rules so recommendations account meaningfully for water availability.
3. Review detergent rules to avoid excessive outputs.
4. Validate delicate-fabric spin recommendations.
5. Rerun the same 10,000 scenarios after any controller changes and compare results fairly.

## Interpretation
To be completed using measured results, including where the fuzzy controller differs from or performs worse than the baseline.

## Limitations and Responsible Use
The dataset is synthetic. Results demonstrate behaviour on simulated scenarios and do not establish real-world cleaning effectiveness or energy savings.

## Reproducibility and Evidence
- Dataset: `data/processed/scenarios.csv`
- Baseline implementation: `src/baseline.py`
- Fuzzy controller: `src/fuzzy_controller.py`
- Comparison code and outputs: to be added in Step 4.

## Team Contributions
- Aditya: fuzzy controller integration and comparison.
- Priyanshu: baseline review.
- Nitin: fuzzy-rule review.
- Ajay: comparison chart.
