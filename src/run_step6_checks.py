"""Run every Step 6 check on THIS computer and save the output as evidence.

Run from the project root (with the project environment active):
    python src/run_step6_checks.py

It writes results/step6/*.txt (one file per check) and results/step6/environment.txt,
then prints a short summary. Commit those files as your own test evidence.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "step6"

CHECKS = [
    ("t10_unit_tests", ["-m", "unittest", "-v", "tests.test_product_predict"]),
    ("ui_tests", ["-m", "unittest", "-v", "tests.test_app_ui"]),
    ("regression_fuzzy_coverage", ["tests/test_fuzzy_coverage.py"]),
    ("regression_fuzzy_report", ["tests/test_fuzzy_matches_report.py"]),
    ("regression_validation", ["tests/test_validation.py"]),
    ("regression_generation", ["tests/test_generation_reproducible.py"]),
    ("regression_compare", ["src/compare_controllers.py"]),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    versions = subprocess.run(
        [sys.executable, "-c",
         "import sys, streamlit, pandas, numpy;"
         "print('Python', sys.version.split()[0]);"
         "print('streamlit', streamlit.__version__);"
         "print('pandas', pandas.__version__);"
         "print('numpy', numpy.__version__)"],
        capture_output=True, text=True, cwd=ROOT)
    (OUT / "environment.txt").write_text(versions.stdout + versions.stderr, encoding="utf-8")

    failed = 0
    for name, args in CHECKS:
        run = subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=ROOT)
        text = (run.stdout + run.stderr)
        text = "\n".join(line for line in text.splitlines() if "missing ScriptRunContext" not in line)
        (OUT / f"{name}.txt").write_text(
            f"$ python {' '.join(args)}\n{text}\nexit code {run.returncode}\n", encoding="utf-8")
        failed += run.returncode != 0
        print(f"{'PASS' if run.returncode == 0 else 'FAIL'}  {name}")
    print("\nSaved in results/step6/. Environment:", versions.stdout.strip().replace("\n", ", "))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
