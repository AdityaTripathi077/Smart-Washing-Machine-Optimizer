"""Initial Mamdani fuzzy washing controller (Step 3 prototype).

This is the same logic as notebooks/02_fuzzy_controller.ipynb, moved into a
reusable module. The membership functions and rules are INITIAL design
choices and still need review and tuning.

Usage:
    from fuzzy_controller import washing_controller
    washing_controller(5, 2.0, "delicate", 80)

Run a quick demo from the project root:
    python src/fuzzy_controller.py
"""
import numpy as np

FABRICS = ("delicate", "cotton", "synthetic", "heavy")


def triangular_mf(x, a, b, c):
    """Triangular membership function with optional shoulders (a == b or b == c)."""
    x = np.asarray(x, dtype=float)
    if not (a <= b <= c):
        raise ValueError("Expected a <= b <= c")

    left = np.ones_like(x) if a == b else (x - a) / (b - a)
    right = np.ones_like(x) if b == c else (c - x) / (c - b)

    membership = np.clip(np.minimum(left, right), 0, 1)
    return np.where(x == b, 1.0, membership)


# ---------- Input universes and membership functions ----------
DIRT = np.linspace(0, 10, 101)
LOAD = np.linspace(0.5, 8, 101)
WATER = np.linspace(0, 100, 101)

DIRT_LOW = triangular_mf(DIRT, -5, 0, 5)
DIRT_MEDIUM = triangular_mf(DIRT, 0, 5, 10)
DIRT_HIGH = triangular_mf(DIRT, 5, 10, 15)

LOAD_SMALL = triangular_mf(LOAD, -3.25, 0.5, 4.25)
LOAD_MEDIUM = triangular_mf(LOAD, 0.5, 4.25, 8)
LOAD_LARGE = triangular_mf(LOAD, 4.25, 8, 11.75)

WATER_LOW = triangular_mf(WATER, -50, 0, 50)
WATER_MEDIUM = triangular_mf(WATER, 0, 50, 100)
WATER_HIGH = triangular_mf(WATER, 50, 100, 150)

# ---------- Output universes and membership functions ----------
WASH_TIME = np.linspace(15, 90, 151)        # minutes
WATER_LITRES = np.linspace(20, 100, 161)    # litres
DETERGENT = np.linspace(10, 100, 181)       # ml
SPIN_RPM = np.linspace(400, 1400, 201)      # RPM

TIME_SHORT = triangular_mf(WASH_TIME, 15, 15, 52.5)
TIME_NORMAL = triangular_mf(WASH_TIME, 15, 52.5, 90)
TIME_LONG = triangular_mf(WASH_TIME, 52.5, 90, 90)

WATER_USAGE_LOW = triangular_mf(WATER_LITRES, 20, 20, 60)
WATER_USAGE_MEDIUM = triangular_mf(WATER_LITRES, 20, 60, 100)
WATER_USAGE_HIGH = triangular_mf(WATER_LITRES, 60, 100, 100)

DETERGENT_LOW = triangular_mf(DETERGENT, 10, 10, 55)
DETERGENT_MEDIUM = triangular_mf(DETERGENT, 10, 55, 100)
DETERGENT_HIGH = triangular_mf(DETERGENT, 55, 100, 100)

SPIN_LOW = triangular_mf(SPIN_RPM, 400, 400, 900)
SPIN_MEDIUM = triangular_mf(SPIN_RPM, 400, 900, 1400)
SPIN_HIGH = triangular_mf(SPIN_RPM, 900, 1400, 1400)


# ---------- Mamdani helpers ----------
def fuzzify(value, x, membership):
    """Membership degree of a crisp input."""
    return float(np.interp(value, x, membership))


def centroid_defuzzify(x, membership):
    """Convert an aggregated fuzzy output to a crisp value."""
    area = np.sum(membership)
    if area == 0:
        raise ValueError("No fuzzy rule fired; cannot defuzzify.")
    return float(np.sum(x * membership) / area)


def _aggregate(strengths, sets):
    """Clip each output set by its rule strength and combine with maximum."""
    return np.maximum.reduce([np.minimum(s, m) for s, m in zip(strengths, sets)])


def validate_inputs(dirt_score, load_kg, fabric_type, water_availability_pct):
    if not 0 <= dirt_score <= 10:
        raise ValueError("Dirt score must be between 0 and 10.")
    if not 0.5 <= load_kg <= 8:
        raise ValueError("Load must be between 0.5 and 8 kg.")
    if not 0 <= water_availability_pct <= 100:
        raise ValueError("Water availability must be between 0 and 100%.")
    if fabric_type not in FABRICS:
        raise ValueError("Invalid fabric type.")


def washing_controller(dirt_score, load_kg, fabric_type, water_availability_pct):
    """Return fuzzy recommendations as a dict (wash time, water, detergent, spin)."""
    validate_inputs(dirt_score, load_kg, fabric_type, water_availability_pct)

    # Fuzzify inputs
    dl = fuzzify(dirt_score, DIRT, DIRT_LOW)
    dm = fuzzify(dirt_score, DIRT, DIRT_MEDIUM)
    dh = fuzzify(dirt_score, DIRT, DIRT_HIGH)

    ls = fuzzify(load_kg, LOAD, LOAD_SMALL)
    lm = fuzzify(load_kg, LOAD, LOAD_MEDIUM)
    ll = fuzzify(load_kg, LOAD, LOAD_LARGE)

    wl = fuzzify(water_availability_pct, WATER, WATER_LOW)
    wm = fuzzify(water_availability_pct, WATER, WATER_MEDIUM)
    wh = fuzzify(water_availability_pct, WATER, WATER_HIGH)

    # Rule strengths: wash time
    time_short_s = max(min(dl, ls), dl * 0.0)
    time_normal_s = dm
    time_long_s = max(dh, min(dh, ll))

    # Rule strengths: detergent
    det_low_s = dl
    det_medium_s = max(dm, min(dh, ls))
    det_high_s = max(min(dh, ll), dh)

    # Rule strengths: water usage (availability and load)
    water_low_s = max(wl, min(wm, ls))
    water_medium_s = max(min(wm, lm), min(wh, ls))
    water_high_s = max(min(wh, ll), min(wm, ll))

    # Fabric-based spin rules
    if fabric_type == "delicate":
        spin_s = (1, 0, 0)
    elif fabric_type == "synthetic":
        spin_s = (0, 1, 0)
    else:  # cotton, heavy
        spin_s = (0, 0, 1)

    time_mf = _aggregate((time_short_s, time_normal_s, time_long_s),
                         (TIME_SHORT, TIME_NORMAL, TIME_LONG))
    water_mf = _aggregate((water_low_s, water_medium_s, water_high_s),
                          (WATER_USAGE_LOW, WATER_USAGE_MEDIUM, WATER_USAGE_HIGH))
    det_mf = _aggregate((det_low_s, det_medium_s, det_high_s),
                        (DETERGENT_LOW, DETERGENT_MEDIUM, DETERGENT_HIGH))
    spin_mf = _aggregate(spin_s, (SPIN_LOW, SPIN_MEDIUM, SPIN_HIGH))

    return {
        "wash_time_min": round(centroid_defuzzify(WASH_TIME, time_mf), 2),
        "water_litre": round(centroid_defuzzify(WATER_LITRES, water_mf), 2),
        "detergent_ml": round(centroid_defuzzify(DETERGENT, det_mf), 2),
        "spin_rpm": round(centroid_defuzzify(SPIN_RPM, spin_mf), 2),
    }


if __name__ == "__main__":
    demo = [(2, 2.0, "cotton", 100), (9, 7.0, "heavy", 100), (5, 2.0, "delicate", 80)]
    for case in demo:
        print("Input:", case)
        print("  ->", washing_controller(*case))
    try:
        washing_controller(11, 9.0, "unknown", 110)
    except ValueError as error:
        print("Invalid input rejected:", error)
