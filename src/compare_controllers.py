"""Step 4: reproducible baseline-vs-fuzzy comparison on the prepared scenarios.

Both controllers are run on the SAME 10,000 rows of data/processed/scenarios.csv.
Nothing is random, so no seed is needed (the scenarios themselves were generated with seed 42).

Run from the project root:
    python src/compare_controllers.py

Writes (all in results/):
    step4_comparison_full.csv        one row per scenario, both controllers, flags
    step4_summary.csv                means, differences, % of scenarios where fuzzy is lower
    step4_rates.csv                  shortfall / feasibility rates per group
    step4_*.png                      charts

ASSUMPTIONS (team-defined, NOT manufacturer data) are all in the block below.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from baseline import baseline_controller
from fuzzy_controller import washing_controller

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "scenarios.csv"
RESULTS = ROOT / "results"

# ------------------------------------------------------------------ ASSUMPTIONS
AVAILABLE_WATER_AT_100_PCT = 100.0   # litres supplied when water_availability_pct = 100
DELICATE_MAX_SAFE_SPIN_RPM = 800     # delicate spin above this is treated as unsafe
# Assumed MINIMUM resources needed for an acceptable wash ("cleaning target"):
REQ_TIME_MIN = lambda dirt, load: 20 + 3 * dirt          # minutes
REQ_DETERGENT_ML = lambda dirt, load: 15 + 3 * dirt + 4 * load   # ml
REQ_WATER_L = lambda dirt, load: 5 * load                # litres
# Relative energy index: unitless proxy (NOT kWh). Motor use ~ wash time, heating ~ water.
ENERGY_W_TIME = 0.5                  # weight of wash time (weight of water = 1 - this)
# --------------------------------------------------------------------------------

MEASURES = ["wash_time_min", "water_litre", "detergent_ml", "spin_rpm", "energy_index"]


def categorize(row):
    """Normal / boundary / stress rules from data/reports/data_quality_report.md."""
    d, l, w = row.dirt_score, row.load_kg, row.water_availability_pct
    if d <= 1 or d >= 9 or l <= 0.75 or l >= 7.75 or w <= 5 or w >= 95:
        return "boundary"
    if d >= 8 or l >= 6 or w <= 25:
        return "stress"
    return "normal"


def energy_index(time_min, water_l, w_time=ENERGY_W_TIME):
    return w_time * time_min / 90 + (1 - w_time) * water_l / 100


def run_controllers(df):
    """Run both controllers. Scenarios where the fuzzy controller cannot produce an
    output (no rule fires) are returned separately and excluded from the statistics."""
    rows, failures = [], []
    for r in df.itertuples(index=False):
        args = (r.dirt_score, r.load_kg, r.fabric_type, r.water_availability_pct)
        b = baseline_controller(*args)
        try:
            f = washing_controller(*args)
        except ValueError as error:
            failures.append({"scenario_id": r.scenario_id, "dirt_score": r.dirt_score,
                             "load_kg": r.load_kg, "fabric_type": r.fabric_type,
                             "water_availability_pct": r.water_availability_pct,
                             "category": categorize(r), "fuzzy_error": str(error)})
            continue
        row = {"scenario_id": r.scenario_id, "dirt_score": r.dirt_score, "load_kg": r.load_kg,
               "fabric_type": r.fabric_type, "water_availability_pct": r.water_availability_pct,
               "category": categorize(r)}
        for tag, out in (("baseline", b), ("fuzzy", f)):
            for m in ("wash_time_min", "water_litre", "detergent_ml", "spin_rpm"):
                row[f"{tag}_{m}"] = out[m]
        rows.append(row)
    out = pd.DataFrame(rows)
    for tag in ("baseline", "fuzzy"):
        out[f"{tag}_energy_index"] = energy_index(out[f"{tag}_wash_time_min"], out[f"{tag}_water_litre"])
    return out, pd.DataFrame(failures)


def add_flags(df):
    avail = df["water_availability_pct"] / 100 * AVAILABLE_WATER_AT_100_PCT
    req_t = REQ_TIME_MIN(df.dirt_score, df.load_kg)
    req_d = REQ_DETERGENT_ML(df.dirt_score, df.load_kg)
    req_w = REQ_WATER_L(df.dirt_score, df.load_kg)
    for tag in ("baseline", "fuzzy"):
        df[f"{tag}_water_over_available"] = df[f"{tag}_water_litre"] > avail
        df[f"{tag}_time_short"] = df[f"{tag}_wash_time_min"] < req_t
        df[f"{tag}_detergent_short"] = df[f"{tag}_detergent_ml"] < req_d
        df[f"{tag}_water_short"] = df[f"{tag}_water_litre"] < req_w
        df[f"{tag}_under_cleaned"] = (df[f"{tag}_time_short"] | df[f"{tag}_detergent_short"]
                                      | df[f"{tag}_water_short"])
        df[f"{tag}_delicate_spin_unsafe"] = ((df.fabric_type == "delicate")
                                             & (df[f"{tag}_spin_rpm"] > DELICATE_MAX_SAFE_SPIN_RPM))
    return df


def groups(df):
    yield "overall", "all", df
    for c in ("normal", "boundary", "stress"):
        yield "category", c, df[df.category == c]
    for f in ("delicate", "cotton", "synthetic", "heavy"):
        yield "fabric", f, df[df.fabric_type == f]


def summarize(df):
    rows = []
    for gtype, gval, g in groups(df):
        for m in MEASURES:
            b, f = g[f"baseline_{m}"], g[f"fuzzy_{m}"]
            rows.append({"group_type": gtype, "group": gval, "scenarios": len(g), "measure": m,
                         "baseline_mean": b.mean(), "fuzzy_mean": f.mean(),
                         "difference_fuzzy_minus_baseline": f.mean() - b.mean(),
                         "percent_difference": 100 * (f.mean() - b.mean()) / b.mean(),
                         "pct_scenarios_fuzzy_lower": 100 * (f < b).mean(),
                         "pct_scenarios_fuzzy_higher": 100 * (f > b).mean()})
    return pd.DataFrame(rows).round(2)


def rates(df):
    flags = ["water_over_available", "time_short", "detergent_short", "water_short",
             "under_cleaned", "delicate_spin_unsafe"]
    rows = []
    for gtype, gval, g in groups(df):
        for fl in flags:
            if fl == "delicate_spin_unsafe":
                g_use = g[g.fabric_type == "delicate"]
            else:
                g_use = g
            if len(g_use) == 0:
                continue
            rows.append({"group_type": gtype, "group": gval, "flag": fl, "scenarios": len(g_use),
                         "baseline_pct": 100 * g_use[f"baseline_{fl}"].mean(),
                         "fuzzy_pct": 100 * g_use[f"fuzzy_{fl}"].mean()})
    return pd.DataFrame(rows).round(2)


def energy_sensitivity(df):
    out = []
    for w in (0.3, 0.5, 0.7):
        b = energy_index(df.baseline_wash_time_min, df.baseline_water_litre, w).mean()
        f = energy_index(df.fuzzy_wash_time_min, df.fuzzy_water_litre, w).mean()
        out.append((w, b, f, 100 * (f - b) / b))
    return out


def charts(df, summary):
    cats = ["normal", "boundary", "stress"]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, m, title in zip(axes, ["water_litre", "detergent_ml", "wash_time_min"],
                            ["Mean water (L)", "Mean detergent (ml)", "Mean wash time (min)"]):
        s = summary[(summary.group_type == "category") & (summary.measure == m)].set_index("group").loc[cats]
        x = np.arange(len(cats))
        ax.bar(x - 0.2, s.baseline_mean, 0.4, label="Baseline", color="#9aa5b1")
        ax.bar(x + 0.2, s.fuzzy_mean, 0.4, label="Fuzzy", color="#2f7ed8")
        ax.set_xticks(x); ax.set_xticklabels(cats); ax.set_title(title); ax.grid(axis="y", alpha=.3)
    axes[0].legend()
    fig.suptitle("Baseline vs fuzzy on the same 10,000 scenarios, by category")
    fig.tight_layout(); fig.savefig(RESULTS / "step4_resources_by_category.png", dpi=150); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    diff = df.fuzzy_water_litre - df.baseline_water_litre
    axes[0].hist(diff, bins=60, color="#2f7ed8")
    axes[0].axvline(0, color="k", lw=1)
    axes[0].set_title("Water: fuzzy minus baseline (L), per scenario")
    axes[0].set_xlabel("negative = fuzzy uses less water"); axes[0].set_ylabel("Scenarios")
    sample = df.sample(2000, random_state=42)
    axes[1].scatter(sample.water_availability_pct, sample.fuzzy_water_litre, s=5, alpha=.4, label="Fuzzy water")
    axes[1].plot([0, 100], [0, AVAILABLE_WATER_AT_100_PCT], "r--", label="Available water (assumed)")
    for fab, c in zip(("delicate", "cotton", "synthetic", "heavy"), ("#888", "#aaa", "#bbb", "#ccc")):
        pass
    axes[1].set_title("Fuzzy water vs water availability (2,000 sampled scenarios)")
    axes[1].set_xlabel("water_availability_pct"); axes[1].set_ylabel("litres"); axes[1].legend()
    fig.tight_layout(); fig.savefig(RESULTS / "step4_water_diagnostics.png", dpi=150); plt.close(fig)

    r = rates(df)
    r = r[(r.group_type == "overall")].set_index("flag")
    fig, ax = plt.subplots(figsize=(8.5, 4))
    x = np.arange(len(r))
    ax.bar(x - 0.2, r.baseline_pct, 0.4, label="Baseline", color="#9aa5b1")
    ax.bar(x + 0.2, r.fuzzy_pct, 0.4, label="Fuzzy", color="#2f7ed8")
    ax.set_xticks(x); ax.set_xticklabels([i.replace("_", "\n") for i in r.index], fontsize=8)
    ax.set_ylabel("% of scenarios"); ax.set_title("Assumed-requirement checks (lower is better)")
    ax.legend(); ax.grid(axis="y", alpha=.3)
    fig.tight_layout(); fig.savefig(RESULTS / "step4_requirement_checks.png", dpi=150); plt.close(fig)


def results_ids(failed):
    return failed["scenario_id"].tolist() if len(failed) else []


def main():
    RESULTS.mkdir(exist_ok=True)
    scenarios = pd.read_csv(INPUT)
    all_categories = scenarios.apply(categorize, axis=1).value_counts()
    df, failed = run_controllers(scenarios)
    df = add_flags(df)
    df.round(3).to_csv(RESULTS / "step4_comparison_full.csv", index=False)
    failed.to_csv(RESULTS / "step4_fuzzy_failures.csv", index=False)
    summary, rate_table = summarize(df), rates(df)
    summary.to_csv(RESULTS / "step4_summary.csv", index=False)
    rate_table.to_csv(RESULTS / "step4_rates.csv", index=False)
    charts(df, summary)

    print("STEP 4: BASELINE VS FUZZY ON THE SAME SCENARIOS")
    print("=" * 60)
    print("Scenarios read:", len(scenarios), "| categories (all):", all_categories.to_dict())
    print("Compared (both controllers gave an output):", len(df))
    print("Fuzzy produced NO output (no rule fired):", len(failed), "->", results_ids(failed))
    pd.set_option("display.width", 200)
    print("\nOVERALL MEANS")
    print(summary[summary.group_type == "overall"][
        ["measure", "baseline_mean", "fuzzy_mean", "percent_difference", "pct_scenarios_fuzzy_lower"]
    ].to_string(index=False))
    print("\nMEANS BY CATEGORY (water, detergent, time)")
    print(summary[(summary.group_type == "category") & summary.measure.isin(
        ["water_litre", "detergent_ml", "wash_time_min"])][
        ["group", "measure", "baseline_mean", "fuzzy_mean", "percent_difference"]].to_string(index=False))
    print("\nREQUIREMENT / FEASIBILITY CHECKS (overall, % of scenarios)")
    print(rate_table[rate_table.group_type == "overall"][
        ["flag", "scenarios", "baseline_pct", "fuzzy_pct"]].to_string(index=False))
    print("\nENERGY INDEX SENSITIVITY (time weight): baseline, fuzzy, % change")
    for w, b, f, p in energy_sensitivity(df):
        print(f"  w_time={w}: {b:.3f} -> {f:.3f} ({p:+.1f}%)")


if __name__ == "__main__":
    main()
