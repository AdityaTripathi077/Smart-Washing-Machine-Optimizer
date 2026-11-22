# Step 6: Testing and validation

## Project and environment
- Project: SC02 Smart Washing Machine Decision and Resource Optimizer (Product V1, `app/app.py`).
- Branch: `step-6-testing`.
- Commit tested: `[run: git rev-parse --short HEAD   and enter the result]`
- Python and dependencies: `[run: python --version   and   pip list   and enter the versions used]`. The automated runs saved in `results/step6/environment.txt` used the versions listed there.
- Launch from the repository root: `python -m streamlit run app/app.py`
- Reference input: the "Normal wash" example (dirt 5, load 4.0 kg, cotton, water 100%).

## How the tests were run
- **UI checks** use Streamlit's headless AppTest. It runs the real `app/app.py`, types into the form, clicks the buttons and reads what the screen shows. No browser window is used.
- **Unit checks** use `python -m unittest`.
- **Browser checks** (T01 download and T09b) need a person to use the running app. They are marked NOT RUN until a team member records them.

## Planned tests and results
Each result was observed when the command in the Evidence section was run.

| ID | Input or action | Expected behaviour | Actual result | Status |
|---|---|---|---|---|
| T01 | Normal wash example, click Recommend settings | A table with wash time, water, detergent and spin for both methods, with units. No error. A CSV download button. | Table rows Wash time, Water, Detergent, Spin speed. Baseline 45 / 60 / 50 / 1000, fuzzy 52.5 / 60.0 / 55.0 / 1235. No error. Download button present. | PASS (automated UI test) |
| T02 | Lower boundary: dirt 0, load 0.5, delicate, water 0 | Inputs accepted, result shown. | Accepted. Fuzzy 27.33 min, 0.0 L water, 24.83 ml, 565 rpm. | PASS |
| T03 | Upper boundary: dirt 10, load 8, heavy, water 100 | Inputs accepted, result shown. | Accepted. Fuzzy 77.67 min, 86.83 L, 85.17 ml, 1235 rpm. | PASS |
| T04 | Dirt score 15 | Show the allowed range and no result. | Message `dirt_score: use a value from 0 to 10.` No table. | PASS |
| T05 | Dirt score `abc` | Ask for a number and no result. | Message `dirt_score: enter a number.` No table. | PASS |
| T06 | Clear the Load field | Ask for a value and no result. | Message `load_kg: enter a value.` No table. | PASS |
| T07 | Disposable copy with `src/fuzzy_controller.py` renamed | Explain that the controller file is missing, hide the form. | Message contains `src/fuzzy_controller.py is missing`. Form hidden (0 input fields). No crash. | PASS |
| T08 | Restore the file in the copy and relaunch | The form returns and the normal case works. | No error and the 3 input fields are back. | PASS |
| T09a | Compare the screen table with direct calls to the baseline and fuzzy code for all four examples | Every value agrees. | All values equal (`test_screen_result_equals_direct_controller_calls`, `test_normal_case_shows_both_methods_and_matches_the_code`). | PASS |
| T09b | Download the CSV from the browser and run `python src/compare_step6_predictions.py` | PASS: inputs and outputs match the reference CSV. | The comparison script was checked on the app's export content: it printed PASS for matching data and FAIL for a changed value and for a missing file. The browser download itself has not been recorded. | NOT RUN (browser step) |
| T10 | `python -m unittest -v tests.test_product_predict` | All validation and result checks run and finish with OK. | Ran 15 tests, OK. | PASS |
| T11 | `python -m unittest -v tests.test_app_ui` | All interface checks run and finish with OK. | Ran 9 tests, OK. | PASS |
| T12 | Limited water example (10% water) | Warnings about the supply, fuzzy water capped. | Warnings: below the 20 L needed, fuzzy reduced to the supply, baseline recommends 60 L. Fuzzy water 10.0 L. | PASS |
| T13 | Enter bad data, then fix it and run again | The app recovers. | No error and a table after the fix. | PASS |
| T14 | Earlier tests: `tests/test_fuzzy_coverage.py`, `test_fuzzy_matches_report.py`, `test_validation.py`, `test_generation_reproducible.py`, and `src/compare_controllers.py` | Still pass after the app was added. | All finished with their pass message. Comparison: 10,000 compared, 0 with no output. | PASS |

## Evidence
| Test ID | File path or exact observed output |
|---|---|
| T01-T03, T09a, T12 | `results/step6/ui_tests.txt` (Ran 9 tests, OK) |
| T04-T06, T13 | `results/step6/ui_tests.txt` |
| T07, T08 | `results/step6/ui_tests.txt` (`test_missing_controller_is_explained_then_recovers`) |
| T10 | `results/step6/t10_unit_tests.txt` (Ran 15 tests, OK) |
| T11 | `results/step6/ui_tests.txt` |
| T14 | `results/step6/regression_fuzzy_coverage.txt`, `regression_fuzzy_report.txt`, `regression_validation.txt`, `regression_generation.txt`, `regression_compare.txt` |
| T09b reference | `data/reports/step5_ui_reference_prediction.csv` |
| Environment | `results/step6/environment.txt` |

## Failures, fixes and retests
| Test ID | What failed | What changed and where | Result of repeating the case and a normal case |
|---|---|---|---|
| T01 (development) | The first version of the app printed a Streamlit session-state warning because the fabric list was given both a default index and a stored value. | Removed the `index` argument in `app/app.py`. The default now comes from the stored value only. | The warning no longer appears and the normal case still passes. |

No other failures were found. These checks cover the app and its saved controllers only.

## Known limits
- The browser checks (T01 CSV download and T09b) still need a team member to run the app and save `data/reports/step6_ui_prediction.csv`.
- The tests used the headless Streamlit tool, not real browsers or devices. Screen layout on phones was not tested.
- At 0% water the fuzzy controller recommends 0 L and the app warns that the result is unreliable.
- A match between the screen and the code shows consistency on the tested inputs. It does not show that the recommendations are right for real washing machines. All data and assumptions are simulated.
- The fuzzy rules still ask for more water than the supply in many scenarios (see `docs/STEP-4.md`). The app caps the water and warns, but the rules are not yet tuned.

## Contributions (fill in with what each person actually did)
| Member | Tests, fixes or evidence completed |
|---|---|
| Aditya Tripathi | |
| Ajay Gangwar | |
| Nitin Kumar | |
| Priyanshu Rajput | |
