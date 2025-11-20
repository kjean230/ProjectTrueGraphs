# ===== py graph for spiders, flies, and AQI analysis ===== #
import os
import math
from pathlib import Path
import datetime as dt

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from data_cleaning import (
    clean_observation_csv,
    clean_air_quality_monthly,
    build_monthly_grid,
)

from data_aggregation import (
    aggregate_monthly_counts,
    aggregate_seasonal_counts,
    aggregate_seasonal_aql,
    add_season_column
)

from plotting_file import (
    plot_scatter_spiders_flies_colored,
    plot_abundance_aqi_time_series,
)

from user_input_to_create_graphs import create_graph_from_choice

def main():
    # creating file paths for specific csv files
    # for spiders, flies, and air quality data
    BASE_DIR = Path(__file__).resolve().parent.parent / "ProjectTrueGraphs" / "csv files"

    CSV_FILE_SPIDERS = BASE_DIR / "file_of_spiders - Sheet1.csv"
    CSV_FILE_FLIES = BASE_DIR / "files_of_flies - Sheet1.csv"
    CSV_FILE_AQ = BASE_DIR / "file_of_air_quality.csv"

    # creates a date range for cleaning the dataframes
    # from January 1, 2017 to June 1, 2023
    start = pd.Timestamp("2017-01-01")
    cutoff = pd.Timestamp("2023-06-01")

    # cleaning the spider observation csv file
    # creates the df for spiders
    # creates aggregated monthly counts for spiders
    spider_df = clean_observation_csv(
        CSV_FILE_SPIDERS,
        start=start,
        cutoff=cutoff,
        iconic_taxon="Arachnida",
    )
    spider_monthly = aggregate_monthly_counts(spider_df, count_col="spider_count")

    # cleaning fly data csv file
    # creates the df for flies
    # creates aggregated monthly counts for flies
    fly_df = clean_observation_csv(
        CSV_FILE_FLIES,
        start=start,
        cutoff=cutoff,
        iconic_taxon="Insecta",
    )
    fly_monthly = aggregate_monthly_counts(fly_df, count_col="fly_count")

    # cleaning the air quality CSV file
    # similar format to the other dataframes
    aq_monthly_df = clean_air_quality_monthly(
        CSV_FILE_AQ,
        start=start,
        cutoff=cutoff,
    )

    # building the monthly grid for merging dataframes later on
    base_months = build_monthly_grid(start=start, cutoff=cutoff)
    df_monthly = (
        base_months.merge(spider_monthly, on=["year", "month", "date_month"], how="left")
        .merge(fly_monthly, on=["year", "month", "date_month"], how="left")
        .merge(aq_monthly_df, on=["year", "month", "date_month"], how="left")
    )

    # filling in missing values with 0 for counts
    # for both spiders and flies
    df_monthly["spider_count"] = df_monthly["spider_count"].fillna(0).astype(int)
    df_monthly["fly_count"] = df_monthly["fly_count"].fillna(0).astype(int)

    # need to sort by time for future graphing purposes
    df_monthly = df_monthly.sort_values("date_month").reset_index(drop=True)

    # plotting scatter plots by year for spiders, flies, and AQI
    # getting user input for graph choice
    userGraphs = input("Which kind of graph would you like to see? (scatter/time series/seasonal/bins): ").strip().lower()
    create_graph_from_choice(userGraphs, df_monthly)

if __name__ == "__main__":
    main()