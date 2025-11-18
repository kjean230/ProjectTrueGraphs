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
# Generate the three months for annual
# january, february, and march will have the AQ value that was originally on january 1st
winter_months = [
    pd.Timestamp('2017-01-01'),
    pd.Timestamp('2017-02-01'),
    pd.Timestamp('2017-03-01')
]

expanded_rows = []
for date_month in winter_months:
    expanded_rows.append({
        'year': date_month.year,
        'month': date_month.month,
        'date_month': date_month,
        'data_value': row['data_value']
    })

annual_expanded_df = pd.DataFrame(expanded_rows)
print(annual_expanded_df)

# generate the six months for the summer
# april, may, june, july, august, and september will have the AQ value that was originally on june 1st
summer_months = [
    pd.Timestamp('2017-04-01'),
    pd.Timestamp('2017-05-01'),
    pd.Timestamp('2017-06-01'),
    pd.Timestamp('2017-07-01'),
    pd.Timestamp('2017-08-01'),
    pd.Timestamp('2017-09-01')
]

expanded_rows = []
for date_month in summer_months:
    expanded_rows.append({
        'year': date_month.year,
        'month': date_month.month,
        'date_month': date_month,
        'data_value': row['data_value']
    })

summer_expanded_df = pd.DataFrame(expanded_rows)
print(summer_expanded_df)

# generating the last three months for fall-winter
# october, november, and december will have the AQ value that was originally on december 1st
fall_winter_months = [
    pd.Timestamp('2017-10-01'),
    pd.Timestamp('2017-11-01'),
    pd.Timestamp('2017-12-01')
]

expanded_rows = {}
for date_month in fall_winter_months:
    expanded_rows.append({
        'year': date_month.year,
        'month': date_month.month,
        'date_month': date_month,
        'data_value': row['data_value']
    })

fall_winter_expanded_df = pd.DataFrame(expanded_rows)
print(fall_winter_expanded_df)
