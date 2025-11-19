# data_cleaning.py
"""
Utility functions to clean CSVs and creation of dataframes (spiders, flies, etc.).
"""
from pathlib import Path
from typing import Optional, Union
import pandas as pd

def clean_observation_csv(csv_path: Union[str, Path], 
                          start: pd.Timestamp, 
                          cutoff: pd.Timestamp, 
                          iconic_taxon: Optional[str] = None,) -> pd.DataFrame:
    
    # function to clean csv files 
    # created to improve reusability and lessening code duplication in main analysis scripts
    # creates a path object that will read all csv files passed through function
    # csv must be in string format
    # making sure the columns ('taxon_name' and 'observed_on') exists within the dataframe
    # making sure that we restrict the date range to a certain window for graph creation
    # create year, month, and month-start date columns for future merging of dataframes

    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path, dtype=str)

    if iconic_taxon is not None:
        if "iconic_taxon_name" not in df.columns:
            raise KeyError(f"'iconic_taxon_name' column not found in {csv_path.name}" 
                           "but iconic_taxon filter was provided.")
        df = df[df["iconic_taxon_name"] == iconic_taxon].copy()

    if "observed_on" not in df.columns:
        raise KeyError(f"'observed_on' column not found in {csv_path.name}.")
    
    df['observed_on'] = pd.to_datetime(df["observed_on"], errors="coerce")
    df   = df.dropna(subset=["observed_on"])

    df = df[
        (df["observed_on"] >= start) & (df["observed_on"] <= cutoff)
    ].copy()

    df['year'] = df['observed_on'].dt.year
    df['month'] = df['observed_on'].dt.month
    df['date_month'] = df['observed_on'].values.astype('datetime64[M]')

    return df

def clean_air_quality_monthly(csv_path: Union[str, Path],
                              start: pd.Timestamp,
                              cutoff: pd.Timestamp,) -> pd.DataFrame:
    
    # cleans air quality data to expand seasonal/annual rows to monthly
    # returns monthly average AQI values
    # implemented in this file to make main file cleaner and less cluttered
    # creates a path object that will read all csv files passed through function
    # csv must be in string format
    # Parse start_date to datetime and drop rows with invalid dates
    # matches specific months to certain time periods (Winter, Summer, Annual)
    # matches those time periods to AQ values
    # may need to merge to dataframes later on for analysis
    # returns a sorted dataframe with monthly average AQI values

    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path, dtype=str)

    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df = df.dropna(subset=["start_date"])

    expanded_rows = []

    for _, row in df.iterrows():
        period = row.get("time_period")
        if pd.isnull(period):
            continue

        start_date_row = row["start_date"]
        data_value = row["data_value"]

        # Map time_period to specific months
        if "Winter" in period:
            # Dec of start year, Jan and Feb of next year
            months = [
                start_date_row,
                start_date_row + pd.DateOffset(months=1),
                start_date_row + pd.DateOffset(months=2),
            ]
        elif "Summer" in period:
            # Jun, Jul, Aug of that year
            months = [
                start_date_row,
                start_date_row + pd.DateOffset(months=1),
                start_date_row + pd.DateOffset(months=2),
            ]
        elif "Annual" in period:
            months = [
                pd.Timestamp(f"{start_date_row.year}-{m:02d}-01")
                for m in range(1, 13)
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

    expanded = pd.DataFrame(expanded_rows)

    expanded = expanded[
        (expanded["date_month"] >= start) & (expanded["date_month"] <= cutoff)
    ].reset_index(drop=True)

    expanded["data_value"] = pd.to_numeric(expanded["data_value"], errors="coerce")
    expanded = expanded.dropna(subset=["data_value"])

    monthly_aqi = (
        expanded.groupby(["year", "month", "date_month"])["data_value"]
        .mean()
        .reset_index()
        .rename(columns={"data_value": "aqi_mean"})
    )

    monthly_aqi = monthly_aqi.sort_values(["year", "month"]).reset_index(drop=True)
    return monthly_aqi


def clean_weather_monthly(csv_path: Union[str, Path],
        start: pd.Timestamp,
        cutoff: pd.Timestamp,
        station_name: str,
    ) -> pd.DataFrame:
    
    # similar to AQ cleaning function
    # cleans weather data to return monthly average temperatures for a specific station
    # creates a path object that will read all csv files passed through function
    # csv must be in string format
    # restricts to specific station name
    # restricts to analysis window
    # returns a sorted dataframe with monthly average temperatures

    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path, dtype=str)

    df["date_month"] = pd.to_datetime(df["date_month"], errors="coerce")
    df = df.dropna(subset=["date_month"])

    df["TAVG"] = pd.to_numeric(df["TAVG"], errors="coerce")
    df = df.dropna(subset=["TAVG"])

    df = df[df["station_name"] == station_name].copy()

    df = df[
        (df["date_month"] >= start) & (df["date_month"] <= cutoff)
    ].copy()

    df["year"] = df["date_month"].dt.year
    df["month"] = df["date_month"].dt.month

    monthly_temp = (
        df.groupby(["year", "month", "date_month"])["TAVG"]
        .mean()
        .reset_index()
        .rename(columns={"TAVG": "temp_mean"})
    )

    monthly_temp = monthly_temp.sort_values(["year", "month"]).reset_index(drop=True)
    return monthly_temp

def build_monthly_grid(start: pd.Timestamp, cutoff: pd.Timestamp) -> pd.DataFrame:
    
    # builds a base dataframe with all year/month combinations in the analysis window
    # useful for merging with other dataframes to ensure all months are represented
    # returns a dataframe with date_month, year, and month columns


    all_months = pd.date_range(start=start, end=cutoff, freq="MS")
    base = pd.DataFrame({"date_month": all_months})
    base["year"] = base["date_month"].dt.year
    base["month"] = base["date_month"].dt.month
    return base


