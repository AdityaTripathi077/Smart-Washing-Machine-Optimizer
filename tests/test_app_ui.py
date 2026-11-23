"""Interface tests for Product V1 using Streamlit's headless AppTest (no browser needed).

Run from the project root:
    python -m unittest -v tests.test_app_ui
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import product_predict as pp  # noqa: E402

APP = str(ROOT / "app" / "app.py")


def open_app():
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def click(at, label):
    next(b for b in at.button if b.label == label).click().run()
    return at


def set_inputs(at, dirt, load, fabric, water):
    at.text_input(key="dirt_score").set_value(dirt)
    at.text_input(key="load_kg").set_value(load)
    at.selectbox(key="fabric_type").set_value(fabric)
    at.text_input(key="water_availability_pct").set_value(water)
    return at


def shown_table(at):
    return at.table[0].value


class InterfaceTests(unittest.TestCase):
    def test_first_screen_opens_with_all_inputs(self):
        at = open_app()
        self.assertEqual(at.title[0].value, "Smart Washing Machine Optimizer")
        self.assertEqual([t.key for t in at.text_input], ["dirt_score", "load_kg", "water_availability_pct"])
        self.assertEqual([s.key for s in at.selectbox], ["fabric_type"])
        self.assertIn("Recommend settings", [b.label for b in at.button])

    def test_normal_case_shows_both_methods_and_matches_the_code(self):
        at = click(open_app(), "Recommend settings")
        self.assertEqual(len(at.error), 0)
        table = shown_table(at)
        expected = pp.recommend(pp.EXAMPLES["Normal wash"])
        self.assertEqual(list(table.index), ["Wash time", "Water", "Detergent", "Spin speed"])
        for key, name in pp.OUTPUT_NAMES.items():
            self.assertEqual(float(table.loc[name, "Baseline (fixed preset)"]), float(expected["baseline"][key]))
            self.assertEqual(float(table.loc[name, "Fuzzy controller"]), float(expected["fuzzy"][key]))
        self.assertTrue(at.get("download_button"), "CSV download button is shown")

    def test_boundary_inputs_are_accepted(self):
        for dirt, load, fabric, water in (("0", "0.5", "delicate", "0"), ("10", "8", "heavy", "100")):
            at = set_inputs(open_app(), dirt, load, fabric, water)
            click(at, "Recommend settings")
            self.assertEqual(len(at.error), 0, (dirt, load, fabric, water))
            self.assertEqual(len(at.table), 1)

    def test_out_of_range_shows_message_and_no_result(self):
        at = set_inputs(open_app(), "15", "4", "cotton", "100")
        click(at, "Recommend settings")
        self.assertIn("dirt_score: use a value from 0 to 10.", [e.value for e in at.error])
        self.assertEqual(len(at.table), 0)

    def test_text_in_a_number_field_asks_for_a_number(self):
        at = set_inputs(open_app(), "abc", "4", "cotton", "100")
        click(at, "Recommend settings")
        self.assertIn("dirt_score: enter a number.", [e.value for e in at.error])
        self.assertEqual(len(at.table), 0)

    def test_blank_field_names_the_missing_value(self):
        at = set_inputs(open_app(), "5", "", "cotton", "100")
        click(at, "Recommend settings")
        self.assertIn("load_kg: enter a value.", [e.value for e in at.error])
        self.assertEqual(len(at.table), 0)

    def test_limited_water_example_warns(self):
        at = open_app()
        click(at, "Limited water")
        click(at, "Recommend settings")
        warnings = " ".join(w.value for w in at.warning)
        self.assertIn("below the 20 L needed", warnings)
        self.assertIn("reduced its water to the available supply", warnings)
        self.assertEqual(float(shown_table(at).loc["Water", "Fuzzy controller"]), 10.0)

    def test_after_an_error_a_valid_run_works_again(self):
        at = set_inputs(open_app(), "15", "4", "cotton", "100")
        click(at, "Recommend settings")
        set_inputs(at, "5", "4", "cotton", "100")
        click(at, "Recommend settings")
        self.assertEqual(len(at.error), 0)
        self.assertEqual(len(at.table), 1)


class MissingControllerUITests(unittest.TestCase):
    """T07/T08 equivalent: run the app from a disposable copy with a controller file missing."""

    SCRIPT = (
        "import sys\n"
        "from streamlit.testing.v1 import AppTest\n"
        "at = AppTest.from_file(sys.argv[1], default_timeout=60); at.run()\n"
        "print('EXC', len(at.exception)); print('ERR', ' | '.join(e.value for e in at.error))\n"
        "print('INPUTS', len(at.text_input)); print('BUTTONS', len(at.button))\n"
    )

    def run_copy(self, copy_root):
        out = subprocess.run([sys.executable, "-c", self.SCRIPT, str(copy_root / "app" / "app.py")],
                             capture_output=True, text=True, cwd=copy_root)
        return dict(line.split(" ", 1) for line in out.stdout.strip().splitlines() if " " in line)

    def test_missing_controller_is_explained_then_recovers(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "project"
            (copy / "src").mkdir(parents=True)
            (copy / "app").mkdir()
            for name in ("baseline.py", "fuzzy_controller.py", "product_predict.py"):
                shutil.copy(ROOT / "src" / name, copy / "src" / name)
            shutil.copy(ROOT / "app" / "app.py", copy / "app" / "app.py")

            (copy / "src" / "fuzzy_controller.py").rename(copy / "src" / "fuzzy_controller.py.disabled")
            broken = self.run_copy(copy)
            self.assertEqual(broken["EXC"], "0")
            self.assertIn("src/fuzzy_controller.py is missing", broken["ERR"])
            self.assertEqual(broken["INPUTS"], "0", "the input form is hidden")

            (copy / "src" / "fuzzy_controller.py.disabled").rename(copy / "src" / "fuzzy_controller.py")
            restored = self.run_copy(copy)
            self.assertEqual(restored["ERR"].strip(), "")
            self.assertEqual(restored["INPUTS"], "3")


if __name__ == "__main__":
    unittest.main(verbosity=2)
