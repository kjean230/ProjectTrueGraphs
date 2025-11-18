import os 
import math
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path
import datetime

#creation of a path to the csv file and reading it into spider dataframe 
CSV_FILE = Path(__file__).resolve().parent.parent / "ProjectTrueGraphs" / "csv files" / "file_of_spiders - Sheet1.csv"
spider_df = pd.read_csv(CSV_FILE, dtype=str)
# reading in the other two csv files into dataframes
# reads the csv files for air quality and temperature/weather data
CSV_FILE2 = Path(__file__).resolve().parent.parent / "ProjectTrueGraphs" / "csv files" / "file_of_monthly_weather.csv"
weather_df = pd.read_csv(CSV_FILE2, dtype=str)
CSV_FILE3 = Path(__file__).resolve().parent.parent / "ProjectTrueGraphs" / "csv files" / "file_of_air_quality.csv"
air_quality_df = pd.read_csv(CSV_FILE3, dtype=str)

# creating columns based on observed_on column in file_of_spiders.csv
# using dt in pandas to extract year and month
spider_df['observed_on'] = pd.to_datetime(spider_df['observed_on'])
spider_df['year'] = spider_df['observed_on'].dt.year
spider_df['month'] = spider_df['observed_on'].dt.month
spider_df['date_month'] = spider_df['observed_on'].values.astype('datetime64[M]')

# creating an aggregated dataframe that counts number of spiders observed per month
spider_monthly = (
    spider_df.groupby(['year', 'month', 'date_month'])
    .size()
    .reset_index(name='spider_count')   
)

# creating year and month columns in air quality dataframe
air_quality_df['start_date'] = pd.to_datetime(air_quality_df['start_date'])
air_quality_df['date_month'] = air_quality_df['start_date'].values.astype('datetime64[M]')
air_quality_df['year'] = air_quality_df['start_date'].dt.year
air_quality_df['month'] = air_quality_df['start_date'].dt.month

# creating year and month columns in weather dataframe 
weather_df['date_month'] = pd.to_datetime(weather_df['date_month'])
weather_df['year'] = weather_df['date_month'].dt.year
weather_df['month'] = weather_df['date_month'].dt.month

# merging dataframes together
# merges spider monthly dataframe with air quality and weather dataframes on year, month, and date_month columns
# similar to sql left join
df = pd.merge(spider_monthly, air_quality_df, on =['year', 'month', 'date_month'], how='left').merge(weather_df, on =['year', 'month', 'date_month'], how='left')