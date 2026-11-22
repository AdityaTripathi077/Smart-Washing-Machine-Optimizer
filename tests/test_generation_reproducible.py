"""Step 2 check: the generator reproduces the committed scenarios, and invalid fixtures stay separate.

Run from the project root:
    python tests/test_generation_reproducible.py
"""
import hashlib
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from generate_scenarios import generate_scenarios  # noqa: E402

failures = 0


def check(name, ok):
    global failures
    failures += not ok
    print(f"{'OK   ' if ok else 'ERROR'} {name}")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


invalid_files = sorted(str(p) for p in (ROOT / "data").glob("invalid*"))
before = {p: digest(p) for p in invalid_files if Path(p).is_file()}

regenerated = generate_scenarios()           # seed 42, 10,000 rows (does not write any file)
committed = pd.read_csv(ROOT / "data" / "raw" / "scenarios.csv")
same = len(regenerated) == len(committed) and (
    regenerated.astype(str).values == committed.astype(str).values).all()
check("regenerating with seed 42 reproduces data/raw/scenarios.csv exactly", same)
check("regenerated data has 10,000 rows", len(regenerated) == 10000)
valid_rows = (regenerated["dirt_score"].between(0, 10).all()
              and regenerated["load_kg"].between(0.5, 8.0).all()
              and regenerated["water_availability_pct"].between(0, 100).all()
              and regenerated["fabric_type"].isin(["delicate", "cotton", "synthetic", "heavy"]).all()
              and regenerated["scenario_id"].is_unique and not regenerated.isnull().any().any())
check("regenerated data contains no invalid rows (ranges, categories, unique IDs, no blanks)", valid_rows)
check("invalid fixtures are untouched by regeneration",
      before == {p: digest(p) for p in before} and len(before) > 0)
check("no invalid scenario IDs in the valid dataset",
      not regenerated["scenario_id"].str.startswith(("INVALID", "BAD")).any())

print("\nResult:", "all checks behaved as expected" if not failures else f"{failures} check(s) failed")
sys.exit(1 if failures else 0)
