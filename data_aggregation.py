# data_aggregation.py


import pandas as pd
from pathlib import Path
from typing import Optional, Union
"""
Utility functions to aggregate cleaned observation data (spiders, flies, etc.).
"""

def aggregate_monthly_counts(df: pd.DataFrame, 
                             count_col: str = "count",
                             ) -> pd.DataFrame:
    # function to aggregate monthly counts from cleaned dataframes
    # may be used for spiders, flies, or other observation dataframes
    # allows for future merging with weather and air quality dataframes
    required_cols = {'year', 'month', 'date_month'}
    missing = required_cols - set(df.columns)
    if missing: 
        raise KeyError(f"DataFrame is missing required columns: {missing}")
    monthly = (
        df.groupby(['year', 'month', 'date_month'])
        .size()
        .reset_index(name=count_col)
    )
    return monthly

def add_season_column(df: pd.DataFrame,
                      month_col: str = "month", 
                      season_col: str = "season") -> pd.DataFrame:
        # function to add a season column based on month values
        # winter: January, February, March
        # summer: April, May, June, July, August
        # fall: September, October, November, December
        if month_col not in df.columns:
            raise KeyError(f"DataFrame is missing required column: {month_col}")
        month_series = df[month_col].astype(int)
        def month_to_season(month: int) -> str:
            if month in [1, 2, 3]:
                return "Winter"
            elif month in [4, 5, 6, 7, 8]:
                return "Summer"
            elif month in [9, 10, 11, 12]:
                return "Fall"
            else:
                raise ValueError(f"month is out of range: {month}")
            
        # making a copy of the dataframe to avoid modifying the original
        # then making sure the seasons are in a specific order for future graphing purposes
        df = df.copy
        df[season_col] = month_series.apply(month_to_season)
        season_order = ["Winter", "Summer", "Fall"]
        df[season_col] = pd.Categorical(df[season_col], categories=season_order, ordered=True)
        return df            

def aggregate_seasonal_counts(df: pd.DataFrame, 
                              count_col: str, 
                              season_col: str = "season",
                              out_col: str = None) -> pd.DataFrame:
    
    required_cols = {"year", season_col, count_col}
    missing = required_cols - set(df.columns)
    if missing:
        raise KeyError(f"DataFrame is missing required columns: {missing}")
    if out_col is None:
        out_col = f"{count_col}_season"
    seasonal = (
             df.groupby(['year', season_col])[count_col]
             .sum()
             .reset_index(name=out_col)
             .rename(columns={count_col: out_col})
             .sort_values(['year', season_col])
             .reset_index(drop=True)
        )   
    return seasonal

def aggregate_seasonal_aql(monthly_aql: pd.DataFrame,
                           season_col: str = "season",
                           out_col: str = "aqi_season") -> pd.DataFrame:
    required_cols = {"year", "month", "aqi_mean"}
    missing = required_cols - set(monthly_aql.columns)
    if missing:
          raise KeyError(f"DataFrame is missing required columns: {missing}")
    df = add_season_column(monthly_aql.copy(), month_col="month", season_col=season_col)
    seasonal_aql = (
        df.groupby(['year', season_col])["aqi_mean"]
        .mean()
        .reset_index(name=out_col)
        .sort_values(["year", season_col])
        .reset_index(drop=True)
    ) 
    return seasonal_aql