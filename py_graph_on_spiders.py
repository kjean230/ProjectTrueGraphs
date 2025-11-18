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

# THIS IS FOR THE YEAR 2017 ONLY
expanded_rows = []
for idx, row in air_quality_df.iterrows():
    period = row['time_period']
    if pd.isnull(period):
        continue # skip rows with missing period
    start_date = row['start_date']
    data_value = row['data_value']
    # Convert start_date to pandas Timestamp if not already
    start_date = pd.to_datetime(start_date)
    
    # Decide which months to cover based on period
    if 'Winter' in period:
        # Winter: Dec of start year, Jan and Feb of next year
        months = [
            start_date,
            start_date + pd.DateOffset(months=1),
            start_date + pd.DateOffset(months=2)
        ]
    elif 'Summer' in period:
        # Summer: Jun, Jul, Aug of start year (adjust as needed for your data)
        months = [
            start_date,
            start_date + pd.DateOffset(months=1),
            start_date + pd.DateOffset(months=2)
        ]
    elif 'Annual' in period:
        # Annual: all 12 months of the year
        months = [pd.Timestamp(f'{start_date.year}-{m:02d}-01') for m in range(1, 13)]
    else:
        # If you have other periods, add more logic here
        continue

    # For each covered month, add a row
    for date_month in months:
        expanded_rows.append({
            'year': date_month.year,
            'month': date_month.month,
            'date_month': date_month,
            'data_value': data_value
        })