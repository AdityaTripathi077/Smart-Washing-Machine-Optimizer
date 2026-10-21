
import numpy as np


def triangular_mf(x, a, b, c):
    """Calculate triangular membership values."""
    x = np.asarray(x, dtype=float)

    if not (a <= b <= c):
        raise ValueError("Expected a <= b <= c")

    left = np.ones_like(x) if a == b else (x - a) / (b - a)
    right = np.ones_like(x) if b == c else (c - x) / (c - b)

    membership = np.minimum(left, right)
    membership = np.clip(membership, 0, 1)
    return np.where(x == b, 1.0, membership)


def fuzzify(value, x, membership):
    """Find the membership degree for a crisp input."""
    return float(np.interp(value, x, membership))


def aggregate_rules(activations, output_sets):
    """Aggregate clipped output membership functions."""
    first_name = next(iter(activations))
    x, _ = output_sets[first_name]
    combined = np.zeros_like(x, dtype=float)

    for name, strength in activations.items():
        _, membership = output_sets[name]
        combined = np.maximum(
            combined, np.minimum(strength, membership)
        )

    return combined
    
def centroid_defuzzify(x, membership):
    """Convert a fuzzy output into a crisp value."""
    total = np.sum(membership)

    if total == 0:
        raise ValueError(
            "Empty fuzzy output: check rule activation and membership functions."
        )

    return float(np.sum(x * membership) / total)


def washing_controller(dirt_score, load_kg, fabric_type,
                       water_availability_pct):
    
    # Aggregate and defuzzify outputs
    time_membership = np.maximum.reduce([
        np.minimum(time_short_strength, time_short),
        np.minimum(time_normal_strength, time_normal),
        np.minimum(time_long_strength, time_long)
    ])
    if np.sum(time_membership) == 0:
        time_membership = time_normal.copy()

    water_membership = np.maximum.reduce([
        np.minimum(water_low_strength, water_usage_low),
        np.minimum(water_medium_strength, water_usage_medium),
        np.minimum(water_high_strength, water_usage_high)
    ])
    if np.sum(water_membership) == 0:
        water_membership = water_usage_medium.copy()

    detergent_membership = np.maximum.reduce([
        np.minimum(detergent_low_strength, detergent_low),
        np.minimum(detergent_medium_strength, detergent_medium),
        np.minimum(detergent_high_strength, detergent_high)
    ])
    if np.sum(detergent_membership) == 0:
        detergent_membership = detergent_medium.copy()

    spin_membership = np.maximum.reduce([
        np.minimum(spin_low_strength, spin_low),
        np.minimum(spin_medium_strength, spin_medium),
        np.minimum(spin_high_strength, spin_high)
    ])
    if np.sum(spin_membership) == 0:
        spin_membership = spin_medium.copy()

    return {
        "wash_time_min": round(
            centroid_defuzzify(wash_time, time_membership), 2
        ),
        "water_litre": round(
            centroid_defuzzify(water_litres, water_membership), 2
        ),
        "detergent_ml": round(
            centroid_defuzzify(detergent, detergent_membership), 2
        ),
        "spin_rpm": round(
            centroid_defuzzify(spin_rpm, spin_membership), 2
        )
    }
