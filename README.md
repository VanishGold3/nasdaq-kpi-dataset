# NASDAQ KPI Dataset – Data Card

**Assignment:** KPI Assignment-Dataset
**Course:** Introduction to Key Performance Indicators – Koźmiński University (Management & AI)
**Date:** 28.04.2026
**Student** Stanisław Wielgomas 52438

---

## 1. Source of Data

For this assignment I used Yahoo Finance API through the yfinance library in Python. I picked 5 companies from NASDAQ – I tried to avoid the obvious ones like Apple or Tesla and go for something less typical. Each company has a different time period which was one of the requirements.

| Ticker | Company | Sector | Period |
|--------|---------|--------|--------|
| CELH | Celsius Holdings | Beverages | Jan 2022 – Dec 2023 |
| CWAN | Clearwater Analytics | FinTech | Sep 2021 – Dec 2022 |
| LAUR | Laureate Education | Education | Feb 2021 – Jun 2022 |
| SPSC | SPS Commerce | Supply Chain | Jun 2020 – Dec 2021 |
| HIMS | Hims & Hers Health | Telehealth | Jan 2021 – Sep 2022 |

The dataset has daily Open, High, Low, Close and Volume for each company. Prices are adjusted for splits (auto_adjust=True).

---

## 2. KPIs

### (a) Completeness

I compared actual rows downloaded vs expected trading days in the period. Stock markets have roughly 252 trading days per year so I used that to estimate.

| Ticker | Expected Days | Got | Missing | Score |
|--------|--------------|-----|---------|-------|
| CELH | 501 | 520 | 0 | 100% |
| CWAN | 335 | 348 | 0 | 100% |
| LAUR | 355 | 369 | 0 | 100% |
| SPSC | 399 | 415 | 0 | 100% |
| HIMS | 426 | 442 | 0 | 100% |

No missing data. The actual count is a bit higher than expected because 252 is just an approximation – real number of trading days varies each year.

### (b) Latency

Since these are historical datasets I measured latency as the number of days between the last available data point and today.

| Ticker | Last Date | Days since today |
|--------|-----------|-----------------|
| CELH | 2023-12-29 | 851 |
| CWAN | 2022-12-30 | 1215 |
| LAUR | 2022-06-30 | 1398 |
| SPSC | 2021-12-31 | 1579 |
| HIMS | 2022-09-30 | 1306 |

CELH is the freshest. SPSC ends in 2021 so it's pretty old at this point. For a real-time use case this would matter a lot, but for this kind of research it's acceptable.

### (c) Accuracy

I flagged any day where the price moved more than 25% in a single day – that would likely be a data error. Also checked that High >= Low for every row.

| Ticker | Anomalies (>25%) | H>=L | Score |
|--------|-----------------|------|-------|
| CELH | 0 | pass | 100% |
| CWAN | 0 | pass | 100% |
| LAUR | 0 | pass | 100% |
| SPSC | 0 | pass | 100% |
| HIMS | 0 | pass | 100% |

No problems found. Yahoo Finance tends to be pretty clean for exchange-listed stocks.

### (d) Consistency

Checked whether dates are in chronological order and whether there are any duplicated rows.

| Ticker | Dates in order | Duplicates | Score |
|--------|---------------|------------|-------|
| CELH | yes | 0 | 100% |
| CWAN | yes | 0 | 100% |
| LAUR | yes | 0 | 100% |
| SPSC | yes | 0 | 100% |
| HIMS | yes | 0 | 100% |

---

## 3. Conclusion

Data quality turned out to be pretty solid across all five companies. Completeness, Accuracy and Consistency all came out at 100%. The only real difference between the datasets is Latency – CELH is the most recent (ends late 2023) while SPSC is the oldest (ends 2021).

In terms of price behavior CELH was by far the most volatile during its growth phase in 2022-2023 which makes it interesting for modeling. LAUR was the opposite – very stable and predictable. HIMS was volatile early on after its SPAC listing which was also interesting to see in the data.

If I had to pick datasets for a prediction model I'd go with CELH and HIMS since they have more recent data and more price variation to work with.

Plots are in the /plots/ folder:
- 01_share_prices.png
- 02_volume.png
- 03_returns_dist.png
- 04_kpi_heatmap.png
- 05_volatility.png
