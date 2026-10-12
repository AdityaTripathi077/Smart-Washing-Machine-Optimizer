# Step 3: Mamdani Fuzzy Rules

## 1. Objective

The Mamdani fuzzy controller will use washing conditions to produce adaptive washing recommendations.

## 2. Inputs

- `dirt_score`: 0–10
- `load_kg`: 0.5–8.0 kg
- `fabric_type`: delicate, cotton, synthetic, heavy
- `water_availability_pct`: 0–100%

## 3. Fuzzy Sets

### Dirt Level

- Low
- Medium
- High

### Load Level

- Small
- Medium
- Large

### Water Availability

- Low
- Medium
- High

### Wash Time

- Short
- Normal
- Long

### Detergent Amount

- Low
- Medium
- High

### Spin Speed

- Low
- Medium
- High

## 4. Initial Mamdani Rules

1. IF dirt is Low AND load is Small THEN wash time is Short.
2. IF dirt is Medium THEN wash time is Normal.
3. IF dirt is High THEN wash time is Long.
4. IF dirt is High AND load is Large THEN detergent amount is High.
5. IF dirt is Low THEN detergent amount is Low.
6. IF water availability is Low THEN water usage should be Low.
7. IF fabric is Delicate THEN spin speed is Low.
8. IF fabric is Cotton AND load is Large THEN spin speed is High.
9. IF fabric is Synthetic THEN spin speed is Medium.
10. IF fabric is Heavy AND dirt is High THEN wash time is Long.

## 5. Inference Method

The controller will use Mamdani inference with fuzzy rule evaluation, aggregation of rule outputs, and defuzzification.

The centroid method will be considered for converting fuzzy output sets into crisp recommendations.

## 6. Notes

These are initial design rules and will be reviewed against the test scenarios before implementation. The final controller must define membership functions, output ranges, and handling for every supported fabric category.

