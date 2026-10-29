"""Interactive dashboard for the web-built BLS JOLTS dataset."""

from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed" / "jolts_industry_monthly.csv"

st.set_page_config(page_title="Industry Workforce Turnover", layout="wide")
st.title("Industry Workforce Turnover and Retention Benchmarking")
st.caption("Built directly from the U.S. Bureau of Labor Statistics JOLTS API. No Kaggle or GitHub dataset is used.")
if not DATA.exists():
    st.error("Run `python main.py` once to collect and construct the official web dataset."); st.stop()
data = pd.read_csv(DATA, parse_dates=["date"])
industries = st.sidebar.multiselect("Industries", sorted(data.industry.unique()), default=sorted(data.industry.unique())[:4])
year_range = st.sidebar.slider("Years", int(data.year.min()), int(data.year.max()), (int(data.year.min()), int(data.year.max())))
metric = st.sidebar.selectbox("Measure", ["quits_rate", "job_openings_rate", "hires_rate", "layoffs_discharges_rate"],
                              format_func=lambda x: x.replace("_", " ").title())
filtered = data[data.industry.isin(industries) & data.year.between(*year_range)]
latest_year = int(data.year.max()); latest = data[data.year == latest_year]
one, two, three = st.columns(3)
one.metric("Constructed observations", f"{len(data):,}")
two.metric("Industries", f"{data.industry.nunique()}")
three.metric("Complete years", f"{data.year.nunique()}")
if filtered.empty: st.warning("Select at least one industry."); st.stop()
trend = filtered.groupby(["date", "industry"], as_index=False)[metric].mean().pivot(index="date", columns="industry", values=metric)
st.subheader(metric.replace("_", " ").title())
st.line_chart(trend, y_label="Percent", x_label="Month")
st.subheader(f"Average monthly rates by industry, {latest_year}")
table = latest.groupby("industry", as_index=False)[["quits_rate", "hires_rate", "job_openings_rate", "layoffs_discharges_rate"]].mean().sort_values("quits_rate", ascending=False)
st.dataframe(table.style.format("{:.2f}", subset=table.columns[1:]), hide_index=True, width="stretch")
st.info("Quits are voluntary separations excluding retirements and transfers. Industry benchmarks cannot diagnose why employees leave a specific company.")
