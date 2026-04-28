import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

os.makedirs("plots", exist_ok=True)

companies = {
    "CELH": {"name": "Celsius Holdings", "sector": "Beverages", "start": "2022-01-01", "end": "2023-12-31"},
    "CWAN": {"name": "Clearwater Analytics", "sector": "FinTech", "start": "2021-09-01", "end": "2022-12-31"},
    "LAUR": {"name": "Laureate Education", "sector": "Education", "start": "2021-02-01", "end": "2022-06-30"},
    "SPSC": {"name": "SPS Commerce", "sector": "Supply Chain", "start": "2020-06-01", "end": "2021-12-31"},
    "HIMS": {"name": "Hims & Hers Health", "sector": "Telehealth", "start": "2021-01-21", "end": "2022-09-30"},
}

print("Downloading data...")
all_data = {}
for ticker, info in companies.items():
    df = yf.download(ticker, start=info['start'], end=info['end'], progress=False, auto_adjust=True)
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    all_data[ticker] = df
    print(f"  {ticker}: {len(df)} rows")

print("\n=== KPI RESULTS ===")
kpi_results = {}
for ticker, df in all_data.items():
    info = companies[ticker]
    expected = round((pd.to_datetime(info['end']) - pd.to_datetime(info['start'])).days * 252/365)
    completeness = round(min(len(df)/expected*100, 100), 2)
    missing = int(df.isnull().sum().sum())
    latency = (pd.Timestamp.today() - df.index[-1]).days
    returns = df['Close'].pct_change().dropna()
    anomalies = int((returns.abs() > 0.25).sum())
    accuracy = round(100 - anomalies/len(df)*100, 2)
    consistency = round(100.0 if missing == 0 else 100 - missing/(len(df)*5)*100, 2)

    kpi_results[ticker] = {
        'Completeness (%)': completeness,
        'Latency (days)': int(latency),
        'Accuracy (%)': accuracy,
        'Consistency (%)': consistency,
    }
    print(f"\n{ticker} - {info['name']}")
    for k, v in kpi_results[ticker].items():
        print(f"  {k}: {v}")

print("\n=== DESCRIPTIVE STATS ===")
for ticker, df in all_data.items():
    print(f"\n{ticker}:")
    print(df['Close'].describe().round(2))

colors = ['#2563EB', '#DC2626', '#16A34A', '#D97706', '#7C3AED']
sns.set_style("whitegrid")

# Plot 1 - prices
fig, axes = plt.subplots(3, 2, figsize=(14, 11))
axes = axes.flatten()
for i, (ticker, df) in enumerate(all_data.items()):
    ax = axes[i]
    ax.plot(df.index, df['Close'], color=colors[i], linewidth=1.4)
    ax.fill_between(df.index, df['Close'], alpha=0.1, color=colors[i])
    ax.set_title(f"{ticker} – {companies[ticker]['name']}", fontweight='bold')
    ax.set_ylabel("Close Price (USD)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha='right')
axes[5].axis('off')
plt.suptitle("Share Price History – NASDAQ Companies", fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig("plots/01_share_prices.png", dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot 1")

# Plot 2 - volume
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()
for i, (ticker, df) in enumerate(all_data.items()):
    ax = axes[i]
    monthly = df['Volume'].resample('ME').mean() / 1e6
    ax.bar(monthly.index, monthly.values, width=20, color=colors[i], alpha=0.8)
    ax.set_title(ticker, fontweight='bold')
    ax.set_ylabel("Avg Vol (M)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha='right')
axes[5].axis('off')
plt.suptitle("Monthly Average Trading Volume", fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig("plots/02_volume.png", dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot 2")

# Plot 3 - returns
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()
for i, (ticker, df) in enumerate(all_data.items()):
    ax = axes[i]
    r = df['Close'].pct_change().dropna() * 100
    ax.hist(r, bins=45, color=colors[i], edgecolor='white', alpha=0.85)
    ax.axvline(r.mean(), color='red', lw=1.2, linestyle=':', label=f'mean={r.mean():.2f}%')
    ax.set_title(f"{ticker} – Daily Returns", fontweight='bold')
    ax.set_xlabel("Return (%)")
    ax.legend(fontsize=8)
axes[5].axis('off')
plt.suptitle("Distribution of Daily Returns", fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig("plots/03_returns_dist.png", dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot 3")

# Plot 4 - KPI heatmap
kpi_df = pd.DataFrame({
    t: {
        'Completeness': kpi_results[t]['Completeness (%)'],
        'Accuracy': kpi_results[t]['Accuracy (%)'],
        'Consistency': kpi_results[t]['Consistency (%)'],
        'Latency Score': round(100 - min(kpi_results[t]['Latency (days)'] / 1500 * 100, 100), 1)
    }
    for t in kpi_results
}).T
fig, ax = plt.subplots(figsize=(9, 4))
sns.heatmap(kpi_df, annot=True, fmt='.1f', cmap='RdYlGn', vmin=0, vmax=100, ax=ax, linewidths=0.5)
ax.set_title("KPI Scores by Company", fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig("plots/04_kpi_heatmap.png", dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot 4")

# Plot 5 - volatility
fig, ax = plt.subplots(figsize=(13, 5))
for i, (ticker, df) in enumerate(all_data.items()):
    rv = df['Close'].pct_change().rolling(30).std() * np.sqrt(252) * 100
    ax.plot(df.index, rv, label=ticker, color=colors[i], linewidth=1.6)
ax.set_title("30-Day Rolling Annualised Volatility (%)", fontsize=12, fontweight='bold')
ax.set_ylabel("Volatility (%)")
ax.legend()
plt.tight_layout()
plt.savefig("plots/05_volatility.png", dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot 5")

print("\n[DONE] All complete!")