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
app/         Product V1 (Streamlit app, Step 5)
report/      final report (later)
```

## How to Reproduce the Results

Run these from the project root.

```text
pip install -r requirements.txt

# Step 2: generate the 10,000 scenarios (random seed 42, fixed in src/generate_scenarios.py)
python src/generate_scenarios.py        # writes data/raw/scenarios.csv
python src/prepare_data.py              # writes data/processed/scenarios.csv; invalid rows go to data/processed/rejected_scenarios.csv

# Step 1: validation (PASS on the sample, FAIL on the invalid test row)
python src/validate_data.py
python src/validate_data.py data/invalid_input.csv

# Step 3 / 4: check the fuzzy controller and compare it with the baseline
python tests/test_fuzzy_matches_report.py
python tests/test_fuzzy_coverage.py            # no rule gaps; water never above the supply
python tests/test_validation.py                # valid sample passes, every invalid fixture fails
python tests/test_generation_reproducible.py   # seed 42 reproduces the data; invalid fixtures stay separate
python src/compare_controllers.py       # writes results/step4_*.csv and *.png

# Step 5 / 6: Product V1 app and its tests
python -m streamlit run app/app.py                 # opens the app at http://localhost:8501
python -m unittest -v tests.test_product_predict   # validation and result checks (15 tests)
python -m unittest -v tests.test_app_ui            # interface checks with a headless Streamlit run (9 tests)
python src/check_product_prediction.py             # writes the reference CSV for the UI-vs-code check
python src/compare_step6_predictions.py            # compares it with the CSV downloaded from the app
```

The generator uses `random.seed(42)`, so every run produces the same 10,000 rows. The scenario data is simulated, not measured. Machine capacity (8 kg) is based on the LG T80VBSF1Z; other ranges and presets are team assumptions (see `data/README.md`).
