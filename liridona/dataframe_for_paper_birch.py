# dataframe_for_paper_birch.py

from pathlib import Path
from typing import Optional, Union
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent / "ProjectTrueGraphs" / "liridona" 
CSV_FILE_BIRCH = BASE_DIR / "csv files" / "Paper Birch data.csv"

df = pd.read_csv(CSV_FILE_BIRCH, dtype=str)
print(df)