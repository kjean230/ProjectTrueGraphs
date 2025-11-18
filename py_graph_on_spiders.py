import os
import math
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path
import datetime


# creation of a path to the csv file and reading it into spider dataframe
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


expanded_rows = []
for idx, row in air_quality_df.iterrows():
   period = row['time_period']
   if pd.isnull(period):
       continue
   start_date = pd.to_datetime(row['start_date'])
   data_value = row['data_value']


   # Handle Winter (e.g., "Winter 2017-18" with start_date Dec 2017)
   if 'Winter' in period:
       months = [
           start_date,
           start_date + pd.DateOffset(months=1),
           start_date + pd.DateOffset(months=2)
       ]
   # Handle Summer (e.g., "Summer 2018" with start_date June 2018)
   elif 'Summer' in period:
       months = [
           start_date,
           start_date + pd.DateOffset(months=1),
           start_date + pd.DateOffset(months=2)
       ]
   # Handle Annual (e.g., "Annual Average 2019" with start_date Jan 2019)
   elif 'Annual' in period:
       months = [pd.Timestamp(f'{start_date.year}-{m:02d}-01') for m in range(1, 13)]
   else:
       continue


   for date_month in months:
       expanded_rows.append({
           'year': date_month.year,
           'month': date_month.month,
           'date_month': date_month,
           'data_value': data_value
       })


expanded_air_quality_df = pd.DataFrame(expanded_rows)
start = pd.Timestamp('2017-01-01')
cutoff = pd.Timestamp('2023-06-01')
expanded_air_quality_df = expanded_air_quality_df[(expanded_air_quality_df['date_month'] >= start) & (expanded_air_quality_df['date_month'] <= cutoff)].reset_index(drop=True)
print(expanded_air_quality_df)