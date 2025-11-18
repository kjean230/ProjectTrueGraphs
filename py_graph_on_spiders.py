# py_graph_on_spiders.py
import os
import math
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path
import datetime

# -------------------------------------------------------------------
# Creation of file paths to different CSV files
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent / "ProjectTrueGraphs" / "csv files"

CSV_FILE_SPIDERS = BASE_DIR / "file_of_spiders - Sheet1.csv"
CSV_FILE_WEATHER = BASE_DIR / "file_of_monthly_weather.csv"
CSV_FILE_AQ = BASE_DIR / "file_of_air_quality.csv"

# -------------------------------------------------------------------
# Read CSVs
# -------------------------------------------------------------------
spider_df = pd.read_csv(CSV_FILE_SPIDERS, dtype=str)
weather_df = pd.read_csv(CSV_FILE_WEATHER, dtype=str)
air_quality_df = pd.read_csv(CSV_FILE_AQ, dtype=str)

# -------------------------------------------------------------------
# Global analysis window
# -------------------------------------------------------------------
start = pd.Timestamp("2017-01-01")
cutoff = pd.Timestamp("2023-06-01")  # last AQ datapoint is Summer 2023

# -------------------------------------------------------------------
# STEP 1: Spider data → monthly counts (Arachnida only)
# -------------------------------------------------------------------

# Keep only Arachnida
spider_df = spider_df[spider_df["iconic_taxon_name"] == "Arachnida"].copy()

# Parse observed_on as datetime
spider_df["observed_on"] = pd.to_datetime(spider_df["observed_on"], errors="coerce")
spider_df = spider_df.dropna(subset=["observed_on"])

# Restrict to analysis window
spider_df = spider_df[
    (spider_df["observed_on"] >= start) & (spider_df["observed_on"] <= cutoff)
].copy()

# Create year, month, and month-start date
spider_df["year"] = spider_df["observed_on"].dt.year
spider_df["month"] = spider_df["observed_on"].dt.month
spider_df["date_month"] = spider_df["observed_on"].values.astype("datetime64[M]")

# Aggregate to monthly spider counts
spider_monthly = (
    spider_df.groupby(["year", "month", "date_month"])
    .size()
    .reset_index(name="spider_count")
)

print("spider_monthly head:")
print(spider_monthly.head())
print("spider_monthly tail:")
print(spider_monthly.tail())

# -------------------------------------------------------------------
# STEP 2: Air quality data → expand seasonal/annual rows to monthly
# -------------------------------------------------------------------

# Parse start_date
air_quality_df["start_date"] = pd.to_datetime(
    air_quality_df["start_date"], errors="coerce"
)
air_quality_df = air_quality_df.dropna(subset=["start_date"])

expanded_rows = []
for idx, row in air_quality_df.iterrows():
    period = row["time_period"]
    if pd.isnull(period):
        continue

    start_date_row = pd.to_datetime(row["start_date"])
    data_value = row["data_value"]

    # Handle Winter (e.g., "Winter 2017-18" starting Dec 2017)
    if "Winter" in period:
        # Dec of start year, Jan and Feb of next year
        months = [
            start_date_row,
            start_date_row + pd.DateOffset(months=1),
            start_date_row + pd.DateOffset(months=2),
        ]
    # Handle Summer (e.g., "Summer 2018" starting Jun 2018)
    elif "Summer" in period:
        # Jun, Jul, Aug of that year
        months = [
            start_date_row,
            start_date_row + pd.DateOffset(months=1),
            start_date_row + pd.DateOffset(months=2),
        ]
    # Handle Annual (e.g., "Annual Average 2019" starting Jan 2019)
    elif "Annual" in period:
        months = [
            pd.Timestamp(f"{start_date_row.year}-{m:02d}-01") for m in range(1, 13)
        ]
    else:
        continue

    for date_month in months:
        expanded_rows.append(
            {
                "year": date_month.year,
                "month": date_month.month,
                "date_month": date_month,
                "data_value": data_value,
            }
        )

expanded_air_quality_df = pd.DataFrame(expanded_rows)

# Restrict to analysis window 2017-01 through 2023-06
expanded_air_quality_df = expanded_air_quality_df[
    (expanded_air_quality_df["date_month"] >= start)
    & (expanded_air_quality_df["date_month"] <= cutoff)
].reset_index(drop=True)

# Numeric AQ
expanded_air_quality_df["data_value"] = pd.to_numeric(
    expanded_air_quality_df["data_value"], errors="coerce"
)
expanded_air_quality_df = expanded_air_quality_df.dropna(subset=["data_value"])

# Aggregate to one value per year/month/date_month (mean if duplicates)
monthly_aqi = (
    expanded_air_quality_df.groupby(["year", "month", "date_month"])["data_value"]
    .mean()
    .reset_index()
    .rename(columns={"data_value": "aqi_mean"})
)

monthly_aqi = monthly_aqi.sort_values(["year", "month"]).reset_index(drop=True)

print("monthly_aqi head:")
print(monthly_aqi.head())
print("monthly_aqi tail:")
print(monthly_aqi.tail())

# -------------------------------------------------------------------
# STEP 3: Weather data → monthly mean temperature for LGA
# -------------------------------------------------------------------

# Parse date_month
weather_df["date_month"] = pd.to_datetime(
    weather_df["date_month"], errors="coerce"
)
weather_df = weather_df.dropna(subset=["date_month"])

# Numeric TAVG (Fahrenheit)
weather_df["TAVG"] = pd.to_numeric(weather_df["TAVG"], errors="coerce")
weather_df = weather_df.dropna(subset=["TAVG"])

# Keep only LAGUARDIA AIRPORT, NY US
weather_df = weather_df[
    weather_df["station_name"] == "LAGUARDIA AIRPORT, NY US"
].copy()

# Restrict to analysis window
weather_df = weather_df[
    (weather_df["date_month"] >= start) & (weather_df["date_month"] <= cutoff)
].copy()

# Year, month
weather_df["year"] = weather_df["date_month"].dt.year
weather_df["month"] = weather_df["date_month"].dt.month

# Aggregate to monthly mean temperature (in case of duplicates)
monthly_temp = (
    weather_df.groupby(["year", "month", "date_month"])["TAVG"]
    .mean()
    .reset_index()
    .rename(columns={"TAVG": "temp_mean"})
)

monthly_temp = monthly_temp.sort_values(["year", "month"]).reset_index(drop=True)

print("monthly_temp head:")
print(monthly_temp.head())
print("monthly_temp tail:")
print(monthly_temp.tail())

# -------------------------------------------------------------------
# STEP 4: Build full monthly grid and merge all three sources
# -------------------------------------------------------------------

all_months = pd.date_range(start=start, end=cutoff, freq="MS")
base_months = pd.DataFrame({"date_month": all_months})
base_months["year"] = base_months["date_month"].dt.year
base_months["month"] = base_months["date_month"].dt.month

# Merge spiders (left), AQ, and temperature
df_monthly = (
    base_months.merge(
        spider_monthly, on=["year", "month", "date_month"], how="left"
    )
    .merge(monthly_aqi, on=["year", "month", "date_month"], how="left")
    .merge(monthly_temp, on=["year", "month", "date_month"], how="left")
)

# Treat missing spiders as zero abundance
df_monthly["spider_count"] = df_monthly["spider_count"].fillna(0).astype(int)

# Sort by time
df_monthly = df_monthly.sort_values("date_month").reset_index(drop=True)

print("df_monthly head:")
print(df_monthly.head())
print("df_monthly tail:")
print(df_monthly.tail())
