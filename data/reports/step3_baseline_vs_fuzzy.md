# Step 3: Baseline vs Fuzzy Controller Results

## 1. Objective

Compare the fixed baseline washing model with the initial Mamdani fuzzy controller using the same seven valid test scenarios.

## 2. Baseline Model

The baseline uses fixed presets based on fabric type. It does not adapt its outputs to dirt score, load weight, or water availability.

## 3. Test Results

| Test ID | Fabric | Baseline Time (min) | Fuzzy Time (min) | Baseline Water (L) | Fuzzy Water (L) | Baseline Detergent (ml) | Fuzzy Detergent (ml) | Baseline RPM | Fuzzy RPM |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FUZZY-001 | cotton | 45 | 45.76 | 60 | 60.00 | 50 | 46.95 | 1000 | 1235 |
| FUZZY-002 | synthetic | 35 | 52.50 | 50 | 59.89 | 40 | 55.00 | 800 | 900 |
| FUZZY-003 | heavy | 60 | 65.63 | 75 | 86.06 | 60 | 70.72 | 1200 | 1235 |
| FUZZY-004 | delicate | 30 | 52.50 | 40 | 56.88 | 30 | 55.00 | 600 | 565 |
| FUZZY-005 | cotton | 45 | 55.43 | 60 | 53.95 | 50 | 58.49 | 1000 | 1235 |
| FUZZY-006 | delicate | 30 | 27.33 | 40 | 33.17 | 30 | 24.83 | 600 | 565 |
| FUZZY-007 | heavy | 60 | 77.67 | 75 | 86.83 | 60 | 85.17 | 1200 | 1235 |

## 4. Validation

- Seven valid scenarios produced washing recommendations.
- The invalid test FUZZY-008 was rejected because its dirt score was outside the permitted range.
- Four separate invalid-input checks previously passed for invalid dirt score, load, fabric type, and water availability.

## 5. Observations

- The fuzzy controller produces adaptive outputs, unlike the fixed baseline.
- Some scenarios receive higher water and detergent recommendations than the baseline.
- Delicate fabric receives a lower spin speed than the baseline.
- The results show differences between the models, but do not establish that the fuzzy controller is more efficient or optimal.

## 6. Limitations and Next Steps

- The fuzzy rules and membership functions are initial design choices and require further review.
- The seven scenarios are a small test set and are not sufficient to establish overall performance.
- Water usage, detergent amounts, and spin-speed rules should be checked against the project's intended behaviour.
- Further evaluation should use the same valid scenarios for both controllers and report measurable resource-use outcomes.
- The Genetic Algorithm optimization stage remains to be implemented and evaluated.
