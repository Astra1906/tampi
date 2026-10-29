"""Descriptive industry turnover calculations."""

from __future__ import annotations
import pandas as pd


RATE_COLUMNS = ["quits_rate", "hires_rate", "job_openings_rate", "total_separations_rate", "layoffs_discharges_rate"]


def validate(data: pd.DataFrame) -> None:
    required = {"date", "year", "month", "industry_code", "industry", *RATE_COLUMNS}
    missing = required - set(data.columns)
    if missing or data.empty:
        raise ValueError("Dataset is empty or missing columns: " + ", ".join(sorted(missing)))


def annual_summary(data: pd.DataFrame) -> pd.DataFrame:
    validate(data)
    return data.groupby(["year", "industry"], as_index=False)[RATE_COLUMNS].mean()


def latest_industry_summary(data: pd.DataFrame) -> pd.DataFrame:
    annual = annual_summary(data)
    latest = int(annual["year"].max())
    result = annual[annual["year"] == latest].copy()
    result["openings_minus_quits_pp"] = result["job_openings_rate"] - result["quits_rate"]
    return result.sort_values("quits_rate", ascending=False).reset_index(drop=True)


def industry_trends(data: pd.DataFrame) -> pd.DataFrame:
    validate(data)
    result = data.copy()
    result["date"] = pd.to_datetime(result["date"])
    return result.sort_values(["industry", "date"])


def period_comparison(data: pd.DataFrame) -> pd.DataFrame:
    """Compare three named periods without claiming that the pandemic caused changes."""
    validate(data)
    working = data.copy()
    working["period"] = pd.cut(working["year"], [2015, 2019, 2022, 2025], labels=["2016–2019", "2020–2022", "2023–2025"])
    return working.groupby(["period", "industry"], observed=True, as_index=False)[RATE_COLUMNS].mean()


def build_tables(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {"annual_summary": annual_summary(data), "latest_industry_summary": latest_industry_summary(data),
            "period_comparison": period_comparison(data)}
