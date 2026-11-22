"""Unit tests for the Product V1 logic (validation, baseline-vs-fuzzy result, missing controller).

Run from the project root:
    python -m unittest -v tests.test_product_predict
or
    python tests/test_product_predict.py
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import product_predict as pp  # noqa: E402
from baseline import baseline_controller  # noqa: E402
from fuzzy_controller import washing_controller  # noqa: E402


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.values = {"dirt_score": "5", "load_kg": "4.0", "fabric_type": "cotton", "water_availability_pct": "100"}

    def test_normal_input_is_converted(self):
        clean = pp.validate_inputs(self.values)
        self.assertEqual(clean["dirt_score"], 5.0)
        self.assertEqual(clean["load_kg"], 4.0)
        self.assertEqual(clean["fabric_type"], "cotton")

    def test_boundaries_are_accepted(self):
        for field, low, high in (("dirt_score", "0", "10"), ("load_kg", "0.5", "8"),
                                 ("water_availability_pct", "0", "100")):
            for value in (low, high):
                values = dict(self.values, **{field: value})
                self.assertEqual(pp.validate_inputs(values)[field], float(value), f"{field}={value}")

    def test_out_of_range_is_rejected_with_the_range(self):
        cases = {"dirt_score": ("11", "use a value from 0 to 10."), "load_kg": ("8.5", "use a value from 0.5 to 8."),
                 "water_availability_pct": ("101", "use a value from 0 to 100.")}
        for field, (value, message) in cases.items():
            with self.assertRaises(pp.InputError) as raised:
                pp.validate_inputs(dict(self.values, **{field: value}))
            self.assertEqual(raised.exception.errors[field], message)

    def test_just_outside_the_limits_is_rejected(self):
        for field, value in (("dirt_score", "-0.1"), ("load_kg", "0.4"), ("water_availability_pct", "-1")):
            with self.assertRaises(pp.InputError):
                pp.validate_inputs(dict(self.values, **{field: value}))

    def test_text_is_rejected(self):
        for text in ("abc", "one", "nan", "inf"):
            with self.assertRaises(pp.InputError) as raised:
                pp.validate_inputs(dict(self.values, dirt_score=text))
            self.assertEqual(raised.exception.errors["dirt_score"], "enter a number.")

    def test_blank_is_rejected(self):
        with self.assertRaises(pp.InputError) as raised:
            pp.validate_inputs(dict(self.values, load_kg="  "))
        self.assertEqual(raised.exception.errors["load_kg"], "enter a value.")

    def test_unknown_fabric_is_rejected(self):
        with self.assertRaises(pp.InputError) as raised:
            pp.validate_inputs(dict(self.values, fabric_type="wool"))
        self.assertIn("fabric_type", raised.exception.errors)

    def test_every_problem_is_listed_at_once(self):
        with self.assertRaises(pp.InputError) as raised:
            pp.validate_inputs({"dirt_score": "15", "load_kg": "abc", "fabric_type": "", "water_availability_pct": ""})
        self.assertEqual(set(raised.exception.errors), set(pp.FIELDS))


class RecommendationTests(unittest.TestCase):
    def test_screen_result_equals_direct_controller_calls(self):
        for name, values in pp.EXAMPLES.items():
            result = pp.recommend(values)
            args = (float(values["dirt_score"]), float(values["load_kg"]), values["fabric_type"],
                    float(values["water_availability_pct"]))
            base, fuzzy = baseline_controller(*args), washing_controller(*args)
            for key in pp.OUTPUTS:
                self.assertEqual(result["baseline"][key], base[key], f"{name} baseline {key}")
                self.assertEqual(result["fuzzy"][key], fuzzy[key], f"{name} fuzzy {key}")

    def test_limited_water_is_flagged_and_capped(self):
        result = pp.recommend(pp.EXAMPLES["Limited water"])
        self.assertTrue(result["fuzzy_water_limited"])
        self.assertLessEqual(result["fuzzy"]["water_litre"], result["water_supply_litre"] + 0.01)
        self.assertTrue(result["baseline_water_over_supply"])
        self.assertTrue(any("below" in text for level, text in pp.notes_for(result)))

    def test_plenty_of_water_has_no_water_warning(self):
        result = pp.recommend(pp.EXAMPLES["Normal wash"])
        self.assertFalse(result["fuzzy_water_limited"])
        self.assertFalse(result["baseline_water_over_supply"])

    def test_delicate_spin_stays_gentle(self):
        result = pp.recommend(pp.EXAMPLES["Delicate, dirty"])
        self.assertLessEqual(result["fuzzy"]["spin_rpm"], 800)

    def test_table_has_every_setting_with_units(self):
        rows = pp.result_table(pp.recommend(pp.EXAMPLES["Normal wash"]))
        self.assertEqual([r["Unit"] for r in rows], ["min", "L", "ml", "rpm"])

    def test_csv_export_matches_the_result(self):
        result = pp.recommend(pp.EXAMPLES["Normal wash"])
        header, row = pp.result_to_csv(result).strip().split("\n")
        data = dict(zip(header.split(","), row.split(",")))
        self.assertEqual(float(data["fuzzy_water_litre"]), result["fuzzy"]["water_litre"])
        self.assertEqual(float(data["baseline_wash_time_min"]), result["baseline"]["wash_time_min"])
        self.assertEqual(data["fabric_type"], "cotton")


class MissingControllerTests(unittest.TestCase):
    """The app depends on saved controller files. Missing files must be explained, then recover."""

    def test_missing_fuzzy_file_is_explained_and_recovery_works(self):
        real_src = pp.SRC
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "src"
            fake.mkdir()
            shutil.copy(real_src / "baseline.py", fake / "baseline.py")      # fuzzy_controller.py is missing
            pp.SRC = fake
            try:
                with self.assertRaises(pp.ControllerUnavailable) as raised:
                    pp.load_controllers()
                self.assertIn("src/fuzzy_controller.py is missing", str(raised.exception))
                shutil.copy(real_src / "fuzzy_controller.py", fake / "fuzzy_controller.py")   # restore
                baseline_fn, fuzzy_fn = pp.load_controllers()
                self.assertTrue(callable(baseline_fn) and callable(fuzzy_fn))
            finally:
                pp.SRC = real_src


if __name__ == "__main__":
    unittest.main(verbosity=2)
