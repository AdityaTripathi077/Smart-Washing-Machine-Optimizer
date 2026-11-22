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

## 4. Fuzzy version evaluated (revised after Step 3 and Step 4 feedback)
The comparison uses `src/fuzzy_controller.py` with two fixes, both switchable so the earlier behaviour can still be reproduced:

1. **Rule gaps closed (`complete_rules=True`).** Three rules were added (rules 11 to 13 in `docs/STEP-3-FUZZY-RULES.md`): low dirt with medium load gives a short wash, low dirt with large load gives a normal wash, and high water availability with a medium load gives medium water. A scan of 106,764 valid inputs found 1,504 points with no output under the old rules and none under the new ones.
2. **Limited water handled (`limit_water=True`).** The recommended water is capped at the assumed supply, `water_availability_pct x 100 L / 100`. The result carries `water_limited = True` when the cap applied.

`python tests/test_fuzzy_matches_report.py` checks both versions: with the old settings the controller still matches the 7 accepted Step 3 report cases (7 of 7). With the revised settings 4 of those 7 are unchanged and 3 change on purpose (water in the cases at 20% and 0% availability, and rule 13 for the 7 kg heavy case at 100% availability: 86.06 L to 71.30 L). The three scenarios that used to fail now give an output, and no valid input on the test grid gives an empty result or more water than the supply.

An earlier idea to replace a missing output with a default value was rejected, because it hides the rule gap. The gaps were fixed with rules instead.

## 5. Scenarios where the fuzzy controller gave no output
Before the fix, the fuzzy controller gave no recommendation for 3 of 10,000 valid scenarios: SC02-01166, SC02-01197 and SC02-06352 (the earlier run is kept in the Git history of `results/step4_fuzzy_failures.csv`). The cause was uncovered input combinations, not invalid data:
- SC02-01197 and SC02-06352 have dirt 0 and a large load, so no wash-time rule fired.
- SC02-01166 has a medium load (4.25 kg) with 100% water availability, so no water rule fired.

After the fix, 0 scenarios fail and **all 10,000 are compared** (`results/step4_fuzzy_failures.csv` now has no rows).

## 6. Measures and assumptions
Water, time, detergent and spin come straight from the controllers. The rest are **team-defined assumptions, not manufacturer data**, listed at the top of `src/compare_controllers.py`.

| Measure | Definition (assumption) | Why this form |
|---|---|---|
| Available water | `water_availability_pct x 100 L / 100` | Simple proportional supply; 100 L at full availability |
| Required wash time | `20 + 3 x dirt` min | A base time for fill, agitation and rinse, plus 3 min per dirt point |
| Required detergent | `15 + 3 x dirt + 4 x load` ml | A base dose, more for dirtier and heavier loads |
| Required water | `5 x load` L | Enough water to wet and rinse each kg |
| Under-cleaned | Any one of time, detergent or water below its requirement | |
| Supply below requirement | Available water < required water | No controller can meet both limits here |
| Relative energy index | `0.5 x wash_time/90 + 0.5 x water/100`. Unitless proxy, not kWh and not measured electricity | |
| Delicate spin unsafe | Delicate fabric with spin above 800 rpm | |

These cleaning targets are modelling choices, but two of them are partly supported by manufacturer guidance. LG's manuals for comparable top-loading machines give a detergent dose per litre of water (20 g of concentrated or 30 g of regular detergent per 30 L) and say the right amount depends on the soil level and the size of the load. For fills of 30 to 65 L that is roughly 20 to 65 g. The detergent minimum here runs from 17 to 77 ml (46 ml at dirt 5 and 4 kg), which is the same range if 1 g is treated as about 1 ml. A comparable LG model's service manual lists water levels of roughly 29 to 65 L, so the water minimum of 5 L per kg (at most 40 L at 8 kg) is deliberately a lower bound. The wash-time minimum has no source and remains an assumption. The sources describe comparable LG models, not the T80VBSF1Z, and give dose guidance, not cleaning-performance data (LG T80BKF21P service manual: https://servlib.com/lg/washing-machine/t80bkf21p.html?start=12; LG T2727S0Z manual, page 57: https://www.manualslib.com/manual/1878039/Lg-T2727s0z.html?page=57; LG WTH8006 manual: https://manualmachine.com/lg/wth8006/4583682-user-manual). To show how much the conclusions depend on them, the minimums were also scaled by 0.8 and 1.2 (section 7, `results/step4_requirement_sensitivity.csv`). The energy index is only a proxy for comparing the two controllers; it says nothing about real electricity use.

## 7. Results (all 10,000 scenarios)
| Measure | Baseline mean | Fuzzy mean | Difference | Fuzzy lower in |
|---|---:|---:|---:|---:|
| Wash time (min) | 42.48 | 53.57 | +26.1% | 24.4% of scenarios |
| Water (L) | 56.22 | 42.21 | -24.9% | 66.8% |
| Detergent (ml) | 44.97 | 54.47 | +21.1% | 27.8% |
| Spin (rpm) | 899 | 983 | +9.2% | 25.1% |
| Energy index (proxy) | 0.52 | 0.51 | -1.6% | 49.9% |

**Most of the water difference comes from the supply cap, not from smarter rules.** The fuzzy water was capped in 59.56% of scenarios (5,956). The baseline ignores supply, so it is over the available water in 55.38% of scenarios while the fuzzy controller is over in 0.00%.

The energy index is not a robust saving. At a time weight of 0.5 it is 1.6% lower, but it changes with the weight: -11.4% at 0.3 and +8.9% at 0.7.

By category, fuzzy water is -9.9% (normal), -29.0% (boundary) and -35.7% (stress). Wash time is +21% to +29% and detergent +19% to +26% in all three. By fabric, fuzzy uses less time, water and detergent than the baseline for heavy loads (time -10.4%, water -44.6%, detergent -8.8%) but much more time and detergent for delicate loads (time +78.6%, detergent +81.7%).

| Check (% of scenarios) | Baseline | Fuzzy |
|---|---:|---:|
| Water over the available supply | 55.38 | 0.00 |
| Water capped by the supply | n/a | 59.56 |
| Supply below the required water (unavoidable) | 22.25 | 22.25 |
| Time short | 33.63 | 0.00 |
| Detergent short | 55.11 | 23.47 |
| Water short | 0.00 | 22.25 |
| Under-cleaned (any shortfall) | 56.96 | 37.40 |
| Delicate spin unsafe | 0.00 | 0.00 |

Sensitivity of the under-cleaned result to the assumed minimums (baseline / fuzzy):

| Minimums scaled by | Baseline | Fuzzy | Fuzzy, excluding shortfalls caused by too little supply |
|---|---:|---:|---:|
| 0.8 | 33.99 | 19.70 | 1.62 |
| 1.0 | 56.96 | 37.40 | 15.15 |
| 1.2 | 73.62 | 61.08 | 34.97 |

The fuzzy controller is under-cleaned less often than the baseline at all three scales, so that conclusion does not depend on the exact assumed numbers. Heavy fabric is the exception: it is under-cleaned in 37.0% of fuzzy scenarios against 16.4% for the baseline, because the fuzzy controller gives heavy loads less time, water and detergent.

Charts: `results/step4_resources_by_category.png`, `results/step4_water_diagnostics.png`, `results/step4_requirement_checks.png`. Full per-scenario data: `results/step4_comparison_full.csv`. Summaries: `results/step4_summary.csv`, `results/step4_rates.csv`, `results/step4_requirement_sensitivity.csv`.

## 8. Interpretation
- **Resource savings are only partly shown.** The fuzzy controller uses less water on average, but mainly because the revised controller respects the water supply and the baseline does not. It uses more wash time (+26%) and detergent (+21%). The energy proxy is close to equal and its direction depends on the weight chosen. We do not claim an energy saving.
- **The fuzzy controller adapts to dirt.** Its detergent and time follow the dirt score, which the baseline cannot do. Under the assumed minimums it falls short less often (37.4% vs 57.0%). This is a trade-off of more time and detergent for fewer shortfalls, and the size of the effect depends on the assumptions in section 6.
- **Water is now handled but not optimised.** Fuzzy water follows water availability (correlation 0.94) and load (0.11) but not dirt (0.00). In 22.25% of scenarios the supply is below the assumed requirement; nothing can fix that, and the controller flags it through `water_limited`. When availability is 25% or less (2,606 scenarios) the water is always capped.
- **Delicate fabric** gets a much longer and more detergent-heavy wash than the baseline (time +78.6%, detergent +81.7%), which needs tuning. Delicate spin is fixed at 565 rpm and always safe.

## 9. Rule parameters to tune (next steps)
| # | Parameter | Evidence | Idea to test |
|---|---|---|---|
| 1 | Water rules use availability and load only | Correlation with dirt is 0.00 | Add dirt and fabric to the water rules |
| 2 | Water output set (floor at 20 L) | Water is below the 20 L floor only through the cap | Lower the floor so the rules can ask for less water on easy loads |
| 3 | Time and detergent rules for delicate fabric | Delicate time +78.6%, detergent +81.7% | Add a fabric term so delicate loads stay short and gentle |
| 4 | Time output sets | Mean time +26% | Check the breakpoints of short, normal and long |
| 5 | Heavy fabric rules | 37.0% under-cleaned vs 16.4% for the baseline | Make heavy loads use more time and detergent |
| 6 | Spin sets for cotton and heavy | Cotton 1235 rpm vs 1000 baseline | Review the spin breakpoints |
| 7 | Assumed cleaning minimums and supply | Drive the shortfall and cap results | Confirm or replace with a sourced cleaning target |

Change one parameter at a time and re-run `python src/compare_controllers.py` to see its effect.

## 10. Limitations
- All scenarios are simulated, not measured. Preset values, the water supply, the cleaning minimums and the energy index are team assumptions.
- The energy index is a proxy. It must not be called measured electricity or an energy saving.
- Capping water at the supply keeps the controller feasible but can leave a wash under-cleaned when the supply is small; the controller flags this rather than solving it.
- The fuzzy rules are still initial design choices.

## 11. Member contributions
| Member | Contribution |
|---|---|
| Aditya Tripathi | Wrote the baseline vs fuzzy comparison script, the executed notebook, and the Step 4 result files and charts. Ran the comparison on the 10,000 scenarios. |
| Ajay Gangwar | Reviewed the comparison results and README with the team. Could not access GitHub during Step 4, so his work was shared with the team and uploaded by teammates. His own commits will be added once his login is fixed. |
| Nitin Kumar | Wrote the Step 4 documentation (`docs/STEP-4.md`), added the fuzzy consistency test, uploaded the README and requirements files, and opened the pull request. |
| Priyanshu Rajput | Fixed the fuzzy controller module so it matches the accepted Step 3 report (7 of 7 cases) and uploaded the corrected `fuzzy_controller.py`. |
