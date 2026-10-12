
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
        raise ValueError("Cannot defuzzify an empty membership function")

    return float(np.sum(x * membership) / total)


def washing_controller(dirt_score, load_kg, fabric_type,
                       water_availability_pct):
    """Return initial Mamdani fuzzy washing recommendations."""

    if not 0 <= dirt_score <= 10:
        raise ValueError("Dirt score must be between 0 and 10.")
    if not 0.5 <= load_kg <= 8:
        raise ValueError("Load must be between 0.5 and 8 kg.")
    if not 0 <= water_availability_pct <= 100:
        raise ValueError("Water availability must be between 0 and 100%.")
    if fabric_type not in ["delicate", "cotton", "synthetic", "heavy"]:
        raise ValueError("Invalid fabric type.")

    # Input universes
    dirt = np.linspace(0, 10, 101)
    load = np.linspace(0.5, 8, 101)
    water = np.linspace(0, 100, 101)

    # Input membership functions
    dirt_low = triangular_mf(dirt, -5, 0, 5)
    dirt_medium = triangular_mf(dirt, 0, 5, 10)
    dirt_high = triangular_mf(dirt, 5, 10, 15)

    load_small = triangular_mf(load, -3.25, 0.5, 4.25)
    load_medium = triangular_mf(load, 0.5, 4.25, 8)
    load_large = triangular_mf(load, 4.25, 8, 11.75)

    water_low = triangular_mf(water, -50, 0, 50)
    water_medium = triangular_mf(water, 0, 50, 100)
    water_high = triangular_mf(water, 50, 100, 150)

    # Fuzzify inputs
    dl = fuzzify(dirt_score, dirt, dirt_low)
    dm = fuzzify(dirt_score, dirt, dirt_medium)
    dh = fuzzify(dirt_score, dirt, dirt_high)

    ls = fuzzify(load_kg, load, load_small)
    lm = fuzzify(load_kg, load, load_medium)
    ll = fuzzify(load_kg, load, load_large)

    wl = fuzzify(water_availability_pct, water, water_low)
    wm = fuzzify(water_availability_pct, water, water_medium)
    wh = fuzzify(water_availability_pct, water, water_high)

    # Output universes
    wash_time = np.linspace(15, 90, 151)
    water_litres = np.linspace(20, 100, 161)
    detergent = np.linspace(10, 100, 181)
    spin_rpm = np.linspace(400, 1400, 201)

    # Output membership functions
    time_short = triangular_mf(wash_time, 0, 15, 45)
    time_normal = triangular_mf(wash_time, 30, 52.5, 75)
    time_long = triangular_mf(wash_time, 60, 90, 120)

    water_usage_low = triangular_mf(water_litres, 0, 20, 60)
    water_usage_medium = triangular_mf(water_litres, 40, 60, 80)
    water_usage_high = triangular_mf(water_litres, 60, 100, 140)

    detergent_low = triangular_mf(detergent, -20, 10, 50)
    detergent_medium = triangular_mf(detergent, 30, 55, 80)
    detergent_high = triangular_mf(detergent, 60, 100, 130)

    spin_low = triangular_mf(spin_rpm, 0, 400, 800)
    spin_medium = triangular_mf(spin_rpm, 600, 900, 1200)
    spin_high = triangular_mf(spin_rpm, 1000, 1400, 1800)

    # Rule strengths: wash time
    time_short_strength = min(dl, ls)
    time_normal_strength = dm
    time_long_strength = dh

    # Rule strengths: detergent
    detergent_low_strength = dl
    detergent_medium_strength = dm
    detergent_high_strength = min(dh, ll)

    # Rule strengths: water usage
    water_low_strength = wl
    water_medium_strength = wm
    water_high_strength = wh

    # Rule strengths: spin speed
    if fabric_type == "delicate":
        spin_low_strength, spin_medium_strength, spin_high_strength = 1, 0, 0
    elif fabric_type == "cotton":
        spin_low_strength = 0
        spin_medium_strength = 1 - ll
        spin_high_strength = ll
    elif fabric_type == "synthetic":
        spin_low_strength, spin_medium_strength, spin_high_strength = 0, 1, 0
    else:
        # Initial design assumption for heavy fabric
        spin_low_strength, spin_medium_strength, spin_high_strength = 0, 0, 1

    # Aggregate and defuzzify outputs
    time_membership = np.maximum.reduce([
        np.minimum(time_short_strength, time_short),
        np.minimum(time_normal_strength, time_normal),
        np.minimum(time_long_strength, time_long)
    ])

    water_membership = np.maximum.reduce([
        np.minimum(water_low_strength, water_usage_low),
        np.minimum(water_medium_strength, water_usage_medium),
        np.minimum(water_high_strength, water_usage_high)
    ])

    detergent_membership = np.maximum.reduce([
        np.minimum(detergent_low_strength, detergent_low),
        np.minimum(detergent_medium_strength, detergent_medium),
        np.minimum(detergent_high_strength, detergent_high)
    ])

    spin_membership = np.maximum.reduce([
        np.minimum(spin_low_strength, spin_low),
        np.minimum(spin_medium_strength, spin_medium),
        np.minimum(spin_high_strength, spin_high)
    ])

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
