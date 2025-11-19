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

