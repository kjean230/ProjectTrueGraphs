import os 
import math
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path
import datetime

CSV_FILE = Path(__file__).resolve().parent.parent / "ProjectTrueGraphs" / "csv files" / "file_of_spiders - Sheet1.csv"
spider_df = pd.read_csv(CSV_FILE, dtype=str, )

spider_df['observed_on'] = pd.to_datetime(spider_df['observed_on'])
spider_df['year'] = spider_df['observed_on'].dt.year
spider_df['month'] = spider_df['observed_on'].dt.month
spider_df['date_month'] = spider_df['observed_on'].values.astype('datetime64[M]')