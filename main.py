"""Collect official BLS web data and generate reproducible analysis outputs."""

from pathlib import Path
import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.analysis import build_tables
from src.collect_data import collect

ROOT = Path(__file__).resolve().parent


def create_figures(data: pd.DataFrame, tables: dict[str, pd.DataFrame], output: Path) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    paths = []
    latest = tables["latest_industry_summary"]
    fig, ax = plt.subplots(figsize=(11, 7))
    sns.barplot(data=latest, y="industry", x="quits_rate", color="#197b80", ax=ax)
    ax.set(title=f"Average monthly quits rate by industry, {int(latest.year.iloc[0])}", xlabel="Quits rate (%)", ylabel="")
    for p in ax.patches: ax.text(p.get_width() + .03, p.get_y() + p.get_height()/2, f"{p.get_width():.1f}%", va="center")
    fig.tight_layout(); path = output / "01_latest_quits_rate.png"; fig.savefig(path, dpi=160); plt.close(fig); paths.append(path)
    fig, ax = plt.subplots(figsize=(12, 7))
    annual = tables["annual_summary"]
    sns.lineplot(data=annual, x="year", y="quits_rate", hue="industry", ax=ax)
    ax.set(title="Average monthly quits rate by industry", xlabel="Year", ylabel="Quits rate (%)")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    fig.tight_layout(); path = output / "02_quits_trends.png"; fig.savefig(path, dpi=160); plt.close(fig); paths.append(path)
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.scatterplot(data=latest, x="job_openings_rate", y="quits_rate", hue="industry", s=100, ax=ax)
    ax.set(title=f"Job openings and quits rates, {int(latest.year.iloc[0])}", xlabel="Job openings rate (%)", ylabel="Quits rate (%)")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    fig.tight_layout(); path = output / "03_openings_vs_quits.png"; fig.savefig(path, dpi=160); plt.close(fig); paths.append(path)
    return paths


def run() -> dict:
    data, manifest = collect(ROOT / "data")
    tables = build_tables(data)
    output = ROOT / "outputs"; (output / "tables").mkdir(parents=True, exist_ok=True)
    for name, table in tables.items(): table.to_csv(output / "tables" / f"{name}.csv", index=False)
    figures = create_figures(data, tables, output / "figures")
    latest = tables["latest_industry_summary"]
    highest = latest.iloc[0]
    summary = {"latest_complete_year": int(latest.year.iloc[0]), "highest_quits_industry": highest.industry,
               "highest_quits_rate": float(highest.quits_rate), "observations": len(data),
               "source_manifest": "data/source_manifest.json",
               "outputs": [str(p.relative_to(ROOT)) for p in figures]}
    top_rows = "\n".join(
        f"| {row.industry} | {row.quits_rate:.2f}% | {row.job_openings_rate:.2f}% | {row.hires_rate:.2f}% | {row.layoffs_discharges_rate:.2f}% |"
        for row in latest.itertuples(index=False)
    )
    report = f"""# Industry Workforce Turnover and Retention Benchmarking

## Business objective

Benchmark voluntary turnover across industries, examine changes over time, and compare quits with hiring demand and employer-initiated separations. The goal is to help managers identify useful external benchmarks before investigating their own employee data.

## Dataset constructed from the web

The project requested 55 seasonally adjusted series directly from the U.S. Bureau of Labor Statistics JOLTS Public Data API. It joined five rate measures for eleven industries into {len(data):,} industry-month observations covering {manifest['audit']['date_min']} through {manifest['audit']['date_max']}. Raw API responses are preserved in `data/raw/`; `data/source_manifest.json` records every series ID, retrieval time, source URL, and processed-file SHA-256.

Validation found {manifest['audit']['missing_rate_cells']} missing rate cells and {manifest['audit']['duplicate_keys']} duplicate industry-month keys.

## Latest complete-year findings

The latest complete calendar year is {int(latest.year.iloc[0])}. {highest.industry} has the highest average monthly quits rate among the selected industries at {highest.quits_rate:.2f}%. This is an industry benchmark, not a company attrition prediction.

| Industry | Quits rate | Job openings rate | Hires rate | Layoffs/discharges rate |
|---|---:|---:|---:|---:|
{top_rows}

## Management use

- Compare an organization's monthly voluntary-turnover measure with the matching industry definition and period.
- Investigate persistent gaps with internal exit feedback, tenure, job role, workload, compensation, and manager data.
- Define a retention pilot, comparison group, follow-up period, and cost before estimating impact.
- Treat job openings and hires as labor-demand context. They do not prove why employees quit.

## Limitations

JOLTS provides industry estimates from an establishment survey, not employee-level records. Results cannot answer questions about individual satisfaction, overtime, income, or promotion history. Seasonal adjustment, sampling error, and revisions affect estimates. Cross-industry differences do not establish causal effects, and U.S. benchmarks may not transfer to an Indian employer without validation.

## Sources

- https://api.bls.gov/publicAPI/v2/timeseries/data/
- https://www.bls.gov/jlt/jltover.htm
- https://www.bls.gov/jlt/jltfaq.htm
"""
    (output / "project_report.md").write_text(report, encoding="utf-8")
    summary["outputs"].append("outputs\\project_report.md")
    (output / "analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
