"""Logic behind Product V1 (no Streamlit code here, so it can be tested directly).

It validates the four user inputs, runs the saved fixed-preset baseline and the saved
fuzzy controller on the SAME inputs, and prepares the result for the screen and for CSV
export. Nothing is trained or tuned here.
"""
import importlib
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

FIELDS = ["dirt_score", "load_kg", "fabric_type", "water_availability_pct"]
FABRICS = ("delicate", "cotton", "synthetic", "heavy")
LIMITS = {"dirt_score": (0.0, 10.0), "load_kg": (0.5, 8.0), "water_availability_pct": (0.0, 100.0)}
LABELS = {"dirt_score": "Dirt score (0-10)", "load_kg": "Load (kg, 0.5-8)",
          "fabric_type": "Fabric", "water_availability_pct": "Water availability (%, 0-100)"}

OUTPUTS = ["wash_time_min", "water_litre", "detergent_ml", "spin_rpm"]
OUTPUT_NAMES = {"wash_time_min": "Wash time", "water_litre": "Water",
                "detergent_ml": "Detergent", "spin_rpm": "Spin speed"}
UNITS = {"wash_time_min": "min", "water_litre": "L", "detergent_ml": "ml", "spin_rpm": "rpm"}

# Same assumption as the Step 4 comparison: 100% availability = 100 L of water.
WATER_AT_100_PCT_L = 100.0
MIN_NORMAL_WASH_L = 20.0

EXAMPLES = {
    "Normal wash": {"dirt_score": "5", "load_kg": "4.0", "fabric_type": "cotton", "water_availability_pct": "100"},
    "Limited water": {"dirt_score": "5", "load_kg": "4.0", "fabric_type": "cotton", "water_availability_pct": "10"},
    "Delicate, dirty": {"dirt_score": "8", "load_kg": "2.0", "fabric_type": "delicate", "water_availability_pct": "80"},
    "Boundary (maximum)": {"dirt_score": "10", "load_kg": "8", "fabric_type": "heavy", "water_availability_pct": "100"},
}


class InputError(ValueError):
    """Raised when inputs are missing or invalid. `.errors` maps field name -> message."""

    def __init__(self, errors):
        self.errors = errors
        super().__init__("; ".join(f"{k}: {v}" for k, v in errors.items()))


class ControllerUnavailable(RuntimeError):
    """Raised when the saved baseline or fuzzy controller cannot be loaded."""


def load_controllers():
    """Load the saved baseline and fuzzy controller. Explains clearly if a file is missing."""
    for name in ("baseline", "fuzzy_controller"):
        if not (SRC / f"{name}.py").is_file():
            raise ControllerUnavailable(
                f"The saved controller file src/{name}.py is missing. "
                "Restore the Step 3/4 files from the repository and restart the app.")
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    try:
        baseline = importlib.import_module("baseline").baseline_controller
        fuzzy = importlib.import_module("fuzzy_controller").washing_controller
    except Exception as error:  # broken file, missing dependency, etc.
        raise ControllerUnavailable(
            f"The saved controllers could not be loaded ({type(error).__name__}: {error}). "
            "Check that the dependencies in requirements.txt are installed.") from error
    return baseline, fuzzy


def _to_number(text):
    value = float(str(text).strip())
    if math.isnan(value) or math.isinf(value):
        raise ValueError
    return value


def validate_inputs(values):
    """Return clean typed inputs, or raise InputError listing every problem."""
    errors, clean = {}, {}
    for field in ("dirt_score", "load_kg", "water_availability_pct"):
        raw = values.get(field)
        if raw is None or str(raw).strip() == "":
            errors[field] = "enter a value."
            continue
        try:
            number = _to_number(raw)
        except (ValueError, TypeError):
            errors[field] = "enter a number."
            continue
        low, high = LIMITS[field]
        if not low <= number <= high:
            errors[field] = f"use a value from {low:g} to {high:g}."
            continue
        clean[field] = number
    fabric = values.get("fabric_type")
    if fabric is None or str(fabric).strip() == "":
        errors["fabric_type"] = "choose a fabric."
    elif str(fabric).strip().lower() not in FABRICS:
        errors["fabric_type"] = "choose one of: " + ", ".join(FABRICS) + "."
    else:
        clean["fabric_type"] = str(fabric).strip().lower()
    if errors:
        raise InputError(errors)
    return clean


def recommend(values, controllers=None):
    """Validate, then run baseline and fuzzy on the same inputs. Returns a result dict."""
    clean = validate_inputs(values)
    baseline_fn, fuzzy_fn = controllers or load_controllers()
    args = (clean["dirt_score"], clean["load_kg"], clean["fabric_type"], clean["water_availability_pct"])
    base = {k: baseline_fn(*args)[k] for k in OUTPUTS}
    fz_raw = fuzzy_fn(*args)
    fuzzy = {k: fz_raw[k] for k in OUTPUTS}
    supply = clean["water_availability_pct"] / 100 * WATER_AT_100_PCT_L
    return {
        "inputs": clean,
        "baseline": base,
        "fuzzy": fuzzy,
        "water_supply_litre": round(supply, 2),
        "fuzzy_water_limited": bool(fz_raw.get("water_limited", False)),
        "baseline_water_over_supply": base["water_litre"] > supply + 0.01,
        "supply_below_normal_wash": supply < MIN_NORMAL_WASH_L,
    }


def notes_for(result):
    """Plain-language messages for the screen: (level, text) pairs."""
    notes = []
    if result["supply_below_normal_wash"]:
        notes.append(("warning", f"Water supply ({result['water_supply_litre']:.0f} L) is below the "
                                 f"{MIN_NORMAL_WASH_L:.0f} L needed for a normal wash. Treat any result as unreliable."))
    if result["fuzzy_water_limited"]:
        notes.append(("warning", "The fuzzy controller reduced its water to the available supply "
                                 f"({result['water_supply_litre']:.0f} L)."))
    if result["baseline_water_over_supply"]:
        notes.append(("warning", f"The fixed baseline recommends {result['baseline']['water_litre']} L, which is more "
                                 f"than the available supply ({result['water_supply_litre']:.0f} L). "
                                 "The baseline ignores water availability."))
    notes.append(("info", "The baseline uses only the fabric type (and the load limit). It ignores dirt score and "
                          "water availability by design."))
    return notes


def result_table(result):
    """Rows for the comparison table: setting, unit, baseline, fuzzy, difference."""
    rows = []
    for key in OUTPUTS:
        b, f = result["baseline"][key], result["fuzzy"][key]
        rows.append({"Setting": OUTPUT_NAMES[key], "Unit": UNITS[key],
                     "Baseline (fixed preset)": b, "Fuzzy controller": f,
                     "Difference (fuzzy - baseline)": round(f - b, 2)})
    return rows


def result_to_dict(result):
    """Flat dict of one result, used for CSV export and the reference check."""
    row = dict(result["inputs"])
    for key in OUTPUTS:
        row[f"baseline_{key}"] = result["baseline"][key]
    for key in OUTPUTS:
        row[f"fuzzy_{key}"] = result["fuzzy"][key]
    row["water_supply_litre"] = result["water_supply_litre"]
    row["fuzzy_water_limited"] = result["fuzzy_water_limited"]
    row["baseline_water_over_supply"] = result["baseline_water_over_supply"]
    return row


def result_to_csv(result):
    row = result_to_dict(result)
    return ",".join(row) + "\n" + ",".join(str(v) for v in row.values()) + "\n"
