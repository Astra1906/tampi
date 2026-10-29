import pandas as pd
from src.analysis import latest_industry_summary
from src.config import series_id


def test_series_id_is_constructed_from_documented_parts():
    assert series_id("300000", "QUR") == "JTS300000000000000QUR"


def test_latest_summary_uses_latest_complete_year():
    rows=[]
    for year, industry, q in [(2024,"A",2.0),(2025,"A",3.0),(2025,"B",4.0)]:
        rows.append({"date":f"{year}-01-01","year":year,"month":1,"industry_code":industry,"industry":industry,
                     "quits_rate":q,"hires_rate":2,"job_openings_rate":5,"total_separations_rate":3,"layoffs_discharges_rate":1})
    result=latest_industry_summary(pd.DataFrame(rows))
    assert result.year.nunique()==1 and result.year.iloc[0]==2025
    assert result.iloc[0].industry=="B"
