# Industry Workforce Turnover and Retention Benchmarking

This project constructs its own dataset directly from the official U.S. Bureau of Labor Statistics Job Openings and Labor Turnover Survey (JOLTS) Public Data API. It does not use Kaggle or GitHub data.

## Build and run

```powershell
cd D:\coding\project\tapmi\bls_turnover_project
python -m pip install -r requirements.txt
python main.py
python -m streamlit run app.py
```

On Windows, `start_app.bat` provides the same application launch and collects the official data first when needed.

`python main.py` requests 55 documented, seasonally adjusted BLS series: five rates for eleven industries over 2016–2025. It preserves each raw JSON response, constructs a tidy monthly CSV, validates completeness and ranges, saves provenance with the exact series IDs and retrieval timestamp, creates analysis tables, and saves three figures.

## Business question

Which industries show persistently high voluntary turnover, how have quits rates changed over time, and how do quits compare with hiring demand, job openings, and employer-initiated separations?

The analysis helps managers benchmark internal turnover against an industry context. It cannot explain why employees leave a specific company or prove that an intervention will improve retention.

## Verified dataset and finding

- 1,320 industry-month observations
- 11 industries and 5 rate measures
- January 2016 through December 2025
- No missing rate cells or duplicate industry-month keys
- Highest 2025 average monthly quits rate among the selected industries: Leisure and hospitality, 3.93%

The calculated tables are saved under `outputs/tables/`, and the figures are saved under `outputs/figures/`.

## GitHub and Streamlit deployment

Create the Git repository from this folder so the older IBM project is not included:

```powershell
cd D:\coding\project\tapmi\bls_turnover_project
git init
git add .
git status
git commit -m "Build BLS workforce turnover analytics application"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

For Streamlit Community Cloud, select the repository and `main` branch, then set the application file to `app.py`. The deployed dashboard reads the included processed CSV, so it does not call the BLS API every time a visitor opens the application.

## Source

- U.S. Bureau of Labor Statistics, [JOLTS overview](https://www.bls.gov/jlt/jltover.htm)
- [BLS Public Data API](https://www.bls.gov/developers/)
- [JOLTS definitions and frequently asked questions](https://www.bls.gov/jlt/jltfaq.htm)

The quits rate is voluntary quits during the month divided by employment. Quits exclude retirements and transfers to other locations.
