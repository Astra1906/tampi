"""Collect and construct a monthly industry-turnover dataset from the BLS API."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd

from .config import BLS_API_URL, END_YEAR, METRICS, SERIES, START_YEAR


class CollectionError(RuntimeError):
    """The official source could not provide a complete, usable response."""


def fetch_batch(series_ids: list[str], start_year: int, end_year: int) -> dict:
    payload = json.dumps({"seriesid": series_ids, "startyear": str(start_year), "endyear": str(end_year)}).encode()
    request = Request(BLS_API_URL, data=payload, headers={
        "Content-Type": "application/json", "User-Agent": "MAHE-IP-Python-course-project/1.0"
    })
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=45) as response:
                result = json.load(response)
            if result.get("status") != "REQUEST_SUCCEEDED":
                raise CollectionError("BLS API response failed: " + "; ".join(result.get("message", [])))
            return result
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = error
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise CollectionError(f"BLS API could not be reached after three attempts: {last_error}")


def parse_responses(responses: list[dict]) -> pd.DataFrame:
    """Join official series into one row per industry and month."""
    records = []
    for response in responses:
        for series in response["Results"]["series"]:
            sid = series["seriesID"]
            if sid not in SERIES:
                raise CollectionError(f"Unexpected series returned: {sid}")
            industry_code, industry, metric = SERIES[sid]
            for item in series.get("data", []):
                period = item.get("period", "")
                if not period.startswith("M") or period == "M13":
                    continue
                value = pd.to_numeric(item.get("value"), errors="coerce")
                records.append({
                    "date": f"{int(item['year']):04d}-{int(period[1:]):02d}-01",
                    "year": int(item["year"]), "month": int(period[1:]),
                    "industry_code": industry_code, "industry": industry,
                    "metric": metric, "value": value, "series_id": sid,
                    "footnote_codes": ",".join(note.get("code", "") for note in item.get("footnotes", []) if note.get("code")),
                })
    long = pd.DataFrame(records)
    if long.empty:
        raise CollectionError("The BLS response contained no monthly observations.")
    duplicates = long.duplicated(["date", "industry_code", "metric"])
    if duplicates.any():
        raise CollectionError("Duplicate industry-month-metric observations were returned.")
    wide = long.pivot(index=["date", "year", "month", "industry_code", "industry"], columns="metric", values="value").reset_index()
    wide.columns.name = None
    expected = set(METRICS.values())
    missing_columns = expected - set(wide.columns)
    if missing_columns:
        raise CollectionError("Missing metric columns: " + ", ".join(sorted(missing_columns)))
    return wide.sort_values(["date", "industry"]).reset_index(drop=True)


def validate_dataset(data: pd.DataFrame, start_year: int, end_year: int) -> dict:
    expected_rows = len({value[0] for value in SERIES.values()}) * (end_year - start_year + 1) * 12
    keys = ["date", "industry_code"]
    if data.duplicated(keys).any():
        raise CollectionError("Constructed data have duplicate industry-month rows.")
    metric_columns = list(METRICS.values())
    invalid = ((data[metric_columns] < 0) | (data[metric_columns] > 100)).sum().sum()
    if invalid:
        raise CollectionError(f"Constructed data contain {int(invalid)} rate values outside 0–100.")
    missing = int(data[metric_columns].isna().sum().sum())
    if len(data) != expected_rows or missing:
        raise CollectionError(f"Incomplete dataset: expected {expected_rows} rows with no missing rates; got {len(data)} rows and {missing} missing rates.")
    return {"rows": len(data), "columns": len(data.columns), "expected_rows": expected_rows,
            "missing_rate_cells": missing, "duplicate_keys": int(data.duplicated(keys).sum()),
            "date_min": data["date"].min(), "date_max": data["date"].max(),
            "industries": int(data["industry_code"].nunique())}


def collect(output_dir: Path, start_year: int = START_YEAR, end_year: int = END_YEAR) -> tuple[pd.DataFrame, dict]:
    """Download raw responses, construct CSV data, and save provenance."""
    output_dir = Path(output_dir)
    raw_dir = output_dir / "raw"
    processed_dir = output_dir / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    ids = list(SERIES)
    responses = []
    for number, start in enumerate(range(0, len(ids), 20), start=1):
        response = fetch_batch(ids[start:start + 20], start_year, end_year)
        responses.append(response)
        (raw_dir / f"bls_response_{number:02d}.json").write_text(json.dumps(response, indent=2), encoding="utf-8")
    data = parse_responses(responses)
    audit = validate_dataset(data, start_year, end_year)
    csv_path = processed_dir / "jolts_industry_monthly.csv"
    data.to_csv(csv_path, index=False)
    digest = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    manifest = {"source": "U.S. Bureau of Labor Statistics JOLTS Public Data API",
                "source_url": BLS_API_URL, "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                "start_year": start_year, "end_year": end_year, "series_count": len(ids),
                "series_ids": ids, "processed_sha256": digest, "audit": audit}
    (output_dir / "source_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return data, manifest
