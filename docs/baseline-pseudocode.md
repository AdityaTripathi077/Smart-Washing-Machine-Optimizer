# Baseline Pseudocode

## Purpose

The baseline uses fixed washing presets for different fabric types.

It does not use Fuzzy Logic or Genetic Algorithm.

## Inputs

- Dirt score
- Load in kg
- Fabric type
- Water availability

## Process

1. Read the user's washing information.
2. Check the load.
3. If the load is greater than 8 kg, show an error.
4. Identify the fabric type.
5. Select the fixed preset for that fabric.
6. Show the washing recommendations.

## Fixed Presets

| Fabric Type | Wash Time | Water | Detergent | Spin Speed |
|---|---:|---:|---:|---:|
| delicate | 30 min | 50 L | 40 ml | 600 RPM |
| cotton | 45 min | 60 L | 60 ml | 1000 RPM |
| synthetic | 40 min | 55 L | 50 ml | 800 RPM |
| heavy | 55 min | 70 L | 70 ml | 1000 RPM |

## Pseudocode

```text
START

Read dirt_score
Read load_kg
Read fabric_type
Read water_availability_pct

IF load_kg > 8:
    Show "Error: Load exceeds machine capacity"
    STOP

IF fabric_type is delicate:
    use delicate preset

ELSE IF fabric_type is cotton:
    use cotton preset

ELSE IF fabric_type is synthetic:
    use synthetic preset

ELSE IF fabric_type is heavy:
    use heavy preset

ELSE:
    Show "Invalid fabric type"
    STOP

Display wash time
Display water usage
Display detergent amount
Display spin speed

END
