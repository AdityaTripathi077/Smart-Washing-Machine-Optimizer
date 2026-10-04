import random
import pandas as pd

OUTPUT_FILE = "data/raw/scenarios.csv"

FABRICS = ["delicate", "cotton", "synthetic", "heavy"]

NUM_SCENARIOS = 10000


def generate_scenarios(n=NUM_SCENARIOS):
    random.seed(42)

    scenarios = []

    for i in range(1, n + 1):
        dirt_score = round(random.uniform(0, 10), 2)
        load_kg = round(random.uniform(0.5, 8.0), 2)
        fabric_type = random.choice(FABRICS)
        water_availability_pct = random.randint(0, 100)

        scenarios.append({
            "scenario_id": f"SC02-{i:05d}",
            "dirt_score": dirt_score,
            "load_kg": load_kg,
            "fabric_type": fabric_type,
            "water_availability_pct": water_availability_pct
        })

    return pd.DataFrame(scenarios)


if __name__ == "__main__":
    df = generate_scenarios()

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Generated {len(df)} scenarios.")
    print(f"Saved to {OUTPUT_FILE}")
