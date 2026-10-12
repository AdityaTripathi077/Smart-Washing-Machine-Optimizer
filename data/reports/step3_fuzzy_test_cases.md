# Step 3 Fuzzy Controller Test Cases

## Objective

These test cases will be used to check the future Mamdani fuzzy controller for the Smart Washing Machine Optimizer.

The cases cover normal, boundary, stress, and invalid inputs.

## Test Cases

| Test ID | Dirt Score | Load (kg) | Fabric | Water Availability (%) | Category | Expected Behaviour |
|---|---:|---:|---|---:|---|---|
| FUZZY-001 | 2 | 2.0 | cotton | 100 | Normal | Shorter wash time and lower detergent |
| FUZZY-002 | 5 | 4.0 | synthetic | 60 | Normal | Moderate wash time and detergent |
| FUZZY-003 | 9 | 7.0 | heavy | 100 | Stress | Longer wash time and higher detergent |
| FUZZY-004 | 5 | 2.0 | delicate | 80 | Normal | Low spin speed to protect delicate fabric |
| FUZZY-005 | 7 | 5.0 | cotton | 20 | Stress | Account for limited water availability |
| FUZZY-006 | 0 | 0.5 | delicate | 0 | Boundary | Accept minimum values and handle low water |
| FUZZY-007 | 10 | 8.0 | heavy | 100 | Boundary | Accept maximum valid dirt and load values |
| FUZZY-008 | 11 | 9.0 | unknown | 110 | Invalid | Reject invalid inputs with a validation error |

## Validation Rules

- Dirt score must be between 0 and 10.
- Load must be between 0.5 and 8.0 kg.
- Fabric must be delicate, cotton, synthetic, or heavy.
- Water availability must be between 0 and 100%.
- Invalid inputs must not produce a washing recommendation.

## Evaluation Notes

The expected behaviours are qualitative design expectations, not measured results. They must be checked after the fuzzy controller is implemented.

The test cases should be reused when comparing the baseline and fuzzy controller.
