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
    base_months.merge(spider_monthly, on=["year", "month", "date_month"], how="left")
    .merge(weather_monthly_df, on=['year', 'month', 'date_month'], how='left')
    .merge(air_quality_df, on=['year', 'month', 'date_month'], how='left')
)

# if any spiders are not accounted for, fill those null values with 0
# we can also sort the dataframe by year and month to ensure proper order/readability
df_monthly['spider_count'] = df_monthly['spider_count'].fillna(0)
df_monthly = df_monthly.sort_values("date_month").reset_index(drop=True)

print(df_monthly)


# # ====== now creating graphs below ====== #
# # creating a scatter plot to visualize the relationship between spider counts and average temperature
# df_scatter_temp = df_monthly.dropna(subset=['temp_mean'])
# fig, ax = plt.subplots(figsize=(10, 6))
# for year, group in df_scatter_temp.groupby("year"):
#     group_sorted = group.sort_values("temp_mean")
#     ax.plot(
#         group_sorted["temp_mean"],
#         group_sorted["spider_count"],
#         marker="o",   # keep the points visible
#         label=str(year),
#     )
# ax.set_xlabel("Monthly mean temperature (°F)")
# ax.set_ylabel("Spider abundance (monthly Arachnida observations)")
# ax.set_title("Spider abundance vs temperature by year")
# ax.legend(title="Year")

# fig.tight_layout()
# plt.show()

# ====== creating a twin y-axis line plot ====== #
# left y axis will be arthropod abundance
# right y axis will be average temperature
# x axis will be january to december
# lines will be for each year from 2017 to 2023

# df_plot = df_monthly.dropna(subset=['temp_mean']).copy()
# df_plot["date_month"] = df_plot["date_month"].astype(int)

# month_positions = np.arange(1, 13)
# month_labels = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

# fig, ax1 = plt.subplots(figsize=(8,6))
# ax2 = ax1.twinx()

# years = sorted(df_plot["year"].unique())
# cmap = plt.get_cmap("tab10")
# colors = cmap(np.linspace(0, 1, len(years)))

# for color, year in zip(colors, years):
#     data_year = df_plot[df_plot["year"] == year].sort_values("month")

#     ax1.plot()


# ====== attempt at a time series line plot ====== #
# the x axis will be broken up by section, months and years, for air quality and arthropod abundance
# for instance, january to march will be one section, april to august, sept to dec, etc.
# this would all fall under a section for 2017, then the next section would be for 2018, etc.
# this matches the format for air quality index reporting
# we may need to match up the arthropod abundance to monthly averages for air quality index

