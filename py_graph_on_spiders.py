# ====== py_graph_on_spiders.py ====== #
import os
import math
from pathlib import Path
import datetime as dt

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

# imports functions from other py file to clean and aggregate data
from data_cleaning import (
    clean_observation_csv, 
    aggregate_monthly_counts, 
    clean_air_quality_monthly,
    clean_weather_monthly,
    build_monthly_grid,
)

# creates file paths for specific csv files
try:
    BASE_DIR = Path(__file__).resolve().parent.parent / "ProjectTrueGraphs" / "csv files"

    CSV_FILE_SPIDERS = BASE_DIR / "file_of_spiders - Sheet1.csv"
    CSV_FILE_WEATHER = BASE_DIR / "file_of_monthly_weather.csv"
    CSV_FILE_AQ = BASE_DIR / "file_of_air_quality.csv"
except Exception as e:
    print(f"Error setting up file paths: {e}")
    raise

# creates a start and cutoff date for cleaning the dataframes
# range will be from January 1, 2017 to June 1, 2023
start = pd.Timestamp("2017-01-01")
cutoff = pd.Timestamp("2023-06-01")

# cleans the spider observation csv file
# creates the df for spiders
# creates aggregated monthly counts for spiders
spider_df = clean_observation_csv(
    CSV_FILE_SPIDERS, 
    start=start, 
    cutoff=cutoff, 
    iconic_taxon="Arachnida",
)
spider_monthly = aggregate_monthly_counts(spider_df, count_col="spider_count")

# cleaning the air quality CSV file
# also making a dataframe for spiders as well
# similar format to the spider cleaning functions

air_quality_df = clean_air_quality_monthly(
    CSV_FILE_AQ,
    start=start,
    cutoff=cutoff,
)

# cleaning the weather CSV file
# also making a dataframe for spiders as well
# similar format to the spider cleaning functions
weather_monthly_df = clean_weather_monthly(
    CSV_FILE_WEATHER,
    start=start,
    cutoff=cutoff,
    station_name="LAGUARDIA AIRPORT, NY US"
)

# creating new dataframe that contains all information
# merges the spider monthly counts with weather and air quality dataframes
# uses a left join (similar to sql) to keep all the spider data
base_months = build_monthly_grid(start=start, cutoff=cutoff)
df_monthly = (
    base_months.merge(spider_monthly, on=["year", "month"], how="left")
    .merge(weather_monthly_df, on=['year', 'month', 'date_month'], how='left')
    .merge(air_quality_df, on=['year', 'month', 'date_month'], how='left')
)

# if any spiders are not accounted for, fill those null values with 0
# we can also sort the dataframe by year and month to ensure proper order/readability
df_monthly['spider_count'] = df_monthly['spider_count'].fillna(0)
df_monthly = df_monthly.sort_values(['year', 'month']).reset_index(drop=True)

print(df_monthly)