## Smart Washing Machine Optimizer

Team Name: Smart Spin

## Team Members
1. Aditya Tripathi
2. Ajay Gangwar
3. Nitin Kumar
4. Priyanshu Rajput

## About the Project
This project is about a smart washing machine system that recommends suitable washing settings based on the clothes and water availability.

The system will recommend:

- Wash time
- Water usage
- Detergent amount
- Spin speed

We will use Fuzzy Logic for M1 and Genetic Algorithm for M2.

## Technologies Used

- Python
- Fuzzy Logic
- Genetic Algorithm
- GitHub

## Project Objective

The main aim of this project is to make suitable washing decisions while reducing unnecessary use of water, detergent and energy.

## Project Stages

### M1
Build a fuzzy washing controller and compare it with fixed washing presets.

### M2
Use a Genetic Algorithm to balance washing quality with resource usage and deploy the final application.

## Repository Structure

```text
docs/        project documents (Step 1 contract, Step 3 baseline and fuzzy rules, Step 4 evaluation)
data/        data dictionary, sample and invalid inputs, raw and processed scenarios, reports
src/         Python code
tests/       repeatable checks
notebooks/   executed notebooks
results/     charts, comparison tables, run outputs
app/         Product V1 (later step)
report/      final report (later)
```

## How to Reproduce the Results

Run these from the project root.

```text
pip install -r requirements.txt

# Step 2: generate the 10,000 scenarios (random seed 42, fixed in src/generate_scenarios.py)
python src/generate_scenarios.py        # writes data/raw/scenarios.csv
python src/prepare_data.py              # validates and writes data/processed/scenarios.csv

# Step 3 / 4: check the fuzzy controller and compare it with the baseline
python tests/test_fuzzy_matches_report.py
python src/compare_controllers.py       # writes results/step4_*.csv and *.png
```

The generator uses `random.seed(42)`, so every run produces the same 10,000 rows. The scenario data is simulated, not measured. Machine capacity (8 kg) is based on the LG T80VBSF1Z; other ranges and presets are team assumptions (see `data/README.md`).
