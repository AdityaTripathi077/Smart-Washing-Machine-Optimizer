# Step 3: Baseline Washing Model

## 1. Objective

The baseline model provides fixed washing recommendations based on fabric type. It will be used as a reference for comparing the future Mamdani fuzzy controller.

## 2. Input Fields

- `dirt_score`: 0–10
- `load_kg`: 0.5–8.0 kg
- `fabric_type`: delicate, cotton, synthetic, heavy
- `water_availability_pct`: 0–100%

## 3. Baseline Rules

The baseline uses fixed presets based on fabric type. It does not adjust recommendations according to dirt score or water availability.

| Fabric Type | Wash Time (min) | Water (litres) | Detergent (ml) | Spin Speed (RPM) |
|---|---:|---:|---:|---:|
| delicate | 30 | 40 | 30 | 600 |
| cotton | 45 | 60 | 50 | 1000 |
| synthetic | 35 | 50 | 40 | 800 |
| heavy | 60 | 75 | 60 | 1200 |

**Note:** These are initial team-defined simulation presets, not manufacturer-recommended settings. They will be reviewed and tested during development.

## 4. Validation Rules

- Dirt score must be between 0 and 10.
- Load must be between 0.5 and 8.0 kg.
- Fabric type must be one of the four documented categories.
- Water availability must be between 0 and 100%.
- Invalid inputs must produce a validation error.

## 5. Limitation

The baseline uses fixed outputs for each fabric type. It does not consider how dirty the clothes are, the load weight, or the available water when choosing its preset. The future fuzzy controller will consider these inputs to produce more adaptive recommendations.

## 6. Evaluation

The baseline and fuzzy controller will be tested using the same valid scenarios. Their recommendations and resource usage will be compared.
