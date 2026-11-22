"""Product V1: Smart Washing Machine Decision and Resource Optimizer.

Start from the project root:
    python -m streamlit run app/app.py
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import product_predict as pp  # noqa: E402

st.set_page_config(page_title="Smart Washing Machine Optimizer", page_icon=None, layout="centered")
st.title("Smart Washing Machine Optimizer")
st.caption("Product V1 prototype. Recommends wash time, water, detergent and spin speed, and compares a "
           "fuzzy controller with a fixed-preset baseline. All scenarios are simulated.")

# ---- The app needs the saved controllers. If they are missing, explain and stop. ----
try:
    controllers = pp.load_controllers()
except pp.ControllerUnavailable as error:
    st.error(str(error))
    st.stop()

DEFAULTS = pp.EXAMPLES["Normal wash"]
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)


def load_example(name):
    for key, value in pp.EXAMPLES[name].items():
        st.session_state[key] = value


st.subheader("1. Enter the wash")
st.write("Load an example, or type your own values.")
cols = st.columns(len(pp.EXAMPLES))
for col, name in zip(cols, pp.EXAMPLES):
    col.button(name, key=f"example_{name}", on_click=load_example, args=(name,), use_container_width=True)

with st.form("wash_form"):
    st.text_input(pp.LABELS["dirt_score"], key="dirt_score",
                  help="0 = clean, 10 = extremely dirty")
    st.text_input(pp.LABELS["load_kg"], key="load_kg", help="Weight of the clothes. The machine holds up to 8 kg.")
    st.selectbox(pp.LABELS["fabric_type"], pp.FABRICS, key="fabric_type")
    st.text_input(pp.LABELS["water_availability_pct"], key="water_availability_pct",
                  help="Share of normal water supply available. The model assumes 100% = 100 L.")
    submitted = st.form_submit_button("Recommend settings", type="primary")

if submitted:
    values = {field: st.session_state[field] for field in pp.FIELDS}
    try:
        result = pp.recommend(values, controllers)
    except pp.InputError as error:
        st.subheader("2. Check your inputs")
        for field, message in error.errors.items():
            st.error(f"{field}: {message}")
        st.caption("No recommendation is shown until every input is valid.")
    else:
        st.subheader("2. Recommended settings")
        table = pd.DataFrame(pp.result_table(result))
        st.table(table.set_index("Setting"))

        for level, text in pp.notes_for(result):
            getattr(st, level)(text)

        st.subheader("3. Compare")
        chart = pd.DataFrame(
            {"Baseline": [result["baseline"][k] for k in ("wash_time_min", "water_litre", "detergent_ml")],
             "Fuzzy": [result["fuzzy"][k] for k in ("wash_time_min", "water_litre", "detergent_ml")]},
            index=["Wash time (min)", "Water (L)", "Detergent (ml)"])
        st.bar_chart(chart)

        st.download_button("Download this result as CSV", pp.result_to_csv(result),
                           file_name="washing_recommendation.csv", mime="text/csv")

with st.expander("How to read this"):
    st.markdown(
        "- **Baseline (fixed preset):** one fixed set of settings per fabric. It ignores dirt score and water availability.\n"
        "- **Fuzzy controller:** uses dirt, load, fabric and water availability. Its water never exceeds the supply.\n"
        "- **Difference:** fuzzy minus baseline. A negative number means the fuzzy controller uses less.\n"
        "- **Limits:** prototype only. The data, water supply scale and presets are simulated team assumptions, "
        "not measured values. The fuzzy controller does not yet show overall resource savings "
        "(see `docs/STEP-4.md`). It is not a safety or fabric-care guarantee.")
