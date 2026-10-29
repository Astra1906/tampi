"""Documented BLS JOLTS series selections used to construct the dataset."""

BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
START_YEAR = 2016
END_YEAR = 2025  # latest complete calendar year; avoids partial-year comparisons

INDUSTRIES = {
    "110099": "Mining and logging",
    "230000": "Construction",
    "300000": "Manufacturing",
    "400000": "Trade, transportation, and utilities",
    "510000": "Information",
    "520000": "Financial activities",
    "540099": "Professional and business services",
    "600000": "Private education and health services",
    "700000": "Leisure and hospitality",
    "810000": "Other services",
    "900000": "Government",
}

METRICS = {
    "QUR": "quits_rate",
    "HIR": "hires_rate",
    "JOR": "job_openings_rate",
    "TSR": "total_separations_rate",
    "LDR": "layoffs_discharges_rate",
}


def series_id(industry_code: str, metric_code: str) -> str:
    """Build the official seasonally adjusted JOLTS series identifier."""
    return f"JTS{industry_code}000000000{metric_code}"


SERIES = {
    series_id(industry_code, metric_code): (industry_code, industry, metric)
    for industry_code, industry in INDUSTRIES.items()
    for metric_code, metric in METRICS.items()
}
