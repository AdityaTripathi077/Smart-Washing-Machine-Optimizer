
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
