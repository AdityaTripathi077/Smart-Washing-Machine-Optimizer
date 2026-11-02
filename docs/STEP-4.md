# Step 4: Baseline vs Fuzzy Comparison on the Prepared Scenarios

## 1. Comparison question
On the same 10,000 prepared wash scenarios, does the initial fuzzy controller use less water, wash time, detergent, and a relative energy index than the fixed-preset baseline, and does it meet the assumed cleaning requirements more often?

## 2. Baseline rule
The baseline is the fixed lookup table from Step 3 (`src/baseline.py`, `docs/STEP-3-BASELINE.md`): one preset per fabric type. It ignores `dirt_score` and `water_availability_pct` by design. It is a fair starting point because it is simple, uses no soft computing, and is similar to a real machine's fixed programmes. It is not a final product.

## 3. Same inputs, no tuning on test data
Both controllers read every row of `data/processed/scenarios.csv` (10,000 simulated scenarios, generated with seed 42). Nothing in either controller is random or fitted to this data, so no train/test split and no seed are needed for the comparison. Rules were not tuned in this step.

Run it with:
```text
python src/compare_controllers.py
```
Terminal output is saved in `results/step4_run_output.txt`. The same steps are shown, with outputs, in the executed notebook `notebooks/03_baseline_comparison.ipynb`.

Scenario categories use the rules in `data/reports/data_quality_report.md`. The recomputed counts match that report: normal 3,274, boundary 3,461, stress 3,265.

## 4. Fuzzy version evaluated
The comparison uses `src/fuzzy_controller.py` as provided in this step. It reproduces the seven values in the accepted Step 3 report (`tests/test_fuzzy_matches_report.py`, 7 of 7 match). The earlier module committed on 12 Oct produced 0 of 7 matches, so it was replaced. A later attempt to add fallback values for empty fuzzy outputs was not kept: it silently replaces a missing result with a default, which hides the rule gap. Such scenarios are reported and excluded instead (section 5).

## 5. Scenarios where the fuzzy controller gave no output
The fuzzy controller returned no recommendation ("no fuzzy rule fired") for 3 of 10,000 valid scenarios: SC02-01166, SC02-01197, SC02-06352 (see `results/step4_fuzzy_failures.csv`). They are excluded, so **9,997 scenarios** are compared. This is a rule-coverage gap, not an input error.

## 6. Measures and assumptions
Water, time, detergent, and spin come straight from the controllers. The rest are **team-defined assumptions, not manufacturer data**, and are listed at the top of `src/compare_controllers.py`.

| Measure | Definition (assumption) |
|---|---|
| Relative energy index | `0.5 x wash_time/90 + 0.5 x water/100`. Unitless, not kWh. Time weights 0.3 and 0.7 were also tried. |
| Water over available | Water > `water_availability_pct` x 100 L / 100 |
| Time / detergent / water short | Below an assumed minimum: time `20 + 3 x dirt` min, detergent `15 + 3 x dirt + 4 x load` ml, water `5 x load` L |
| Under-cleaned | Any one of the three shortfalls |
| Delicate spin unsafe | Delicate fabric with spin above 800 rpm |

**The shortfall results depend on the assumed minimums.** They need review before they are quoted as evidence.

## 7. Results (9,997 scenarios)
| Measure | Baseline mean | Fuzzy mean | Difference | Fuzzy lower in |
|---|---:|---:|---:|---:|
| Wash time (min) | 42.48 | 54.78 | +29.0% | 22.7% of scenarios |
| Water (L) | 56.23 | 57.45 | +2.2% | 46.2% |
| Detergent (ml) | 44.97 | 54.48 | +21.1% | 27.8% |
| Spin (rpm) | 899 | 983 | +9.2% | 25.1% |
| Energy index | 0.52 | 0.59 | +14.4% | 30.5% |

The energy result stays higher for the fuzzy controller at every time weight tried (+9.3% to +19.9%).

By category, mean water is +2.1% (normal), 0.0% (boundary), and +4.6% (stress). Mean detergent is +19% to +26% in all three. By fabric, fuzzy uses less water and time than baseline for heavy loads (water -23.9%, time -8.4%) but much more for delicate (water +43.5%, time +82.6%, detergent +81.7%).

| Check (% of scenarios) | Baseline | Fuzzy |
|---|---:|---:|
| Under-cleaned (any shortfall) | 56.97 | 23.48 |
| Detergent short | 55.12 | 23.46 |
| Time short | 33.64 | 0.00 |
| Water short | 0.00 | 0.49 |
| Water over available | 55.39 | 59.57 |
| Delicate spin unsafe | 0.00 | 0.00 |

Under-cleaned by category (baseline / fuzzy): normal 45.0 / 2.1, boundary 56.3 / 27.6, stress 69.7 / 40.6.

Charts: `results/step4_resources_by_category.png`, `results/step4_water_diagnostics.png`, `results/step4_requirement_checks.png`. Full per-scenario data: `results/step4_comparison_full.csv`. Summaries: `results/step4_summary.csv`, `results/step4_rates.csv`.

## 8. Interpretation
- **No resource savings are demonstrated.** On average the fuzzy controller uses slightly more water and clearly more time, detergent, and energy index.
- **The fuzzy controller adapts to dirt.** Its detergent and time correlate strongly with dirt score (0.93 and 0.83), which the baseline cannot do. Under the assumed minimums it falls short much less often (23% vs 57%). This is a trade-off: more resources for fewer shortfalls, and it depends on the assumptions in section 6.
- **Water is the main weakness.** Fuzzy water follows load (correlation 0.57) and availability (0.65) but not dirt (0.01), and it never goes below 33 L, even at 0% availability. When availability is 25% or less (2,606 scenarios), 100% of scenarios exceed the available water for both controllers.
- **Delicate spin** is fixed at 565 rpm for every delicate scenario. It is safe, but it does not vary with the load.

## 9. Rule parameters to tune (Step 4 follow-up)
| # | Parameter | Evidence | Idea to test |
|---|---|---|---|
| 1 | Water output universe floor (20 L) and low-water set | Fuzzy water never below 33 L | Lower the floor or move the low set, then re-run |
| 2 | Water rules use only availability and load | Correlation with dirt is 0.01 | Add dirt and fabric to the water rules; cap water at availability |
| 3 | Rule coverage (medium load with high availability, near-zero dirt) | 3 scenarios give no output | Add rules for the missing combinations, or a fallback |
| 4 | Time and detergent rules for delicate fabric | Delicate time +82.6%, detergent +81.7% | Add a fabric term so delicate loads stay short and gentle |
| 5 | Time output sets | Mean time +29% | Check the breakpoints of short, normal, and long |
| 6 | Spin sets for cotton and heavy | Cotton 1235 rpm vs 1000 baseline | Review the spin breakpoints |
| 7 | Assumed cleaning minimums | Drive the shortfall results | Confirm or replace with a sourced cleaning target |

Change one parameter at a time and re-run `python src/compare_controllers.py` to see its effect.

## 10. Limitations
- All scenarios are simulated, not measured. Preset values, cleaning minimums, and the energy index are team assumptions.
- The energy index is a proxy. It must not be called an energy saving.
- The fuzzy rules are still initial design choices.

## 11. Member contributions
| Member | Contribution |
|---|---|
| Aditya Tripathi | Wrote the baseline vs fuzzy comparison script, the executed notebook, and the Step 4 result files and charts. Ran the comparison on the 10,000 scenarios. |
| Ajay Gangwar | Reviewed the comparison results and README with the team. Could not access GitHub during Step 4, so his work was shared with the team and uploaded by teammates. His own commits will be added once his login is fixed. |
| Nitin Kumar | Wrote the Step 4 documentation (`docs/STEP-4.md`), added the fuzzy consistency test, uploaded the README and requirements files, and opened the pull request. |
| Priyanshu Rajput | Fixed the fuzzy controller module so it matches the accepted Step 3 report (7 of 7 cases) and uploaded the corrected `fuzzy_controller.py`. |
