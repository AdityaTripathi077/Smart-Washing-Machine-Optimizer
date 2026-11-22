"""Repeatable validation test using committed CSV fixtures (no screenshots needed).

Run from the project root:
    python tests/test_validation.py
"""
import subprocess
import sys

CASES = [
    # (file, should_pass, text expected in the output)
    ("data/sample_input.csv", True, "PASS: All data is valid"),
    ("data/invalid/over_capacity.csv", False, "Load must be between 0.5 and 8 kg"),
    ("data/invalid/load_too_small.csv", False, "Load must be between 0.5 and 8 kg"),
    ("data/invalid/dirt_out_of_range.csv", False, "Dirt score must be between 0 and 10"),
    ("data/invalid/water_out_of_range.csv", False, "Water availability must be between 0 and 100"),
    ("data/invalid/unknown_fabric.csv", False, "Invalid fabric type found"),
    ("data/invalid/missing_value.csv", False, "Missing values found"),
    ("data/invalid/duplicate_id.csv", False, "Duplicate scenario ID found"),
    ("data/invalid_input.csv", False, "FAIL"),
]


def main():
    failures = 0
    for file, should_pass, expected_text in CASES:
        run = subprocess.run([sys.executable, "src/validate_data.py", file],
                             capture_output=True, text=True)
        passed_validation = run.returncode == 0
        ok = (passed_validation == should_pass) and expected_text in run.stdout
        failures += not ok
        verdict = "validator PASSED" if passed_validation else "validator FAILED (expected)" if not should_pass else "validator FAILED"
        print(f"{'OK  ' if ok else 'ERROR'} {file}: {verdict}")
    print(f"\nResult: {len(CASES) - failures}/{len(CASES)} checks behaved as expected")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
