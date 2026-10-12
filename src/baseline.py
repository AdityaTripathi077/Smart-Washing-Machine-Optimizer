
"""Fixed-preset baseline for the Smart Washing Machine Optimizer."""

BASELINE_PRESETS = {
    "delicate": {
        "wash_time_min": 30,
        "water_litre": 40,
        "detergent_ml": 30,
        "spin_rpm": 600,
    },
    "cotton": {
        "wash_time_min": 45,
        "water_litre": 60,
        "detergent_ml": 50,
        "spin_rpm": 1000,
    },
    "synthetic": {
        "wash_time_min": 35,
        "water_litre": 50,
        "detergent_ml": 40,
        "spin_rpm": 800,
    },
    "heavy": {
        "wash_time_min": 60,
        "water_litre": 75,
        "detergent_ml": 60,
        "spin_rpm": 1200,
    },
}


def baseline_controller(
    dirt_score,
    load_kg,
    fabric_type,
    water_availability_pct,
):
    """Return fixed washing recommendations for the fabric type."""

    if not 0 <= dirt_score <= 10:
        raise ValueError("Dirt score must be between 0 and 10.")
    if not 0.5 <= load_kg <= 8:
        raise ValueError("Load must be between 0.5 and 8 kg.")
    if not 0 <= water_availability_pct <= 100:
        raise ValueError("Water availability must be between 0 and 100%.")
    if fabric_type not in BASELINE_PRESETS:
        raise ValueError("Invalid fabric type.")

    return BASELINE_PRESETS[fabric_type].copy()
