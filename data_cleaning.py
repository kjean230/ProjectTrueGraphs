# data_cleaning.py
"""
Utility functions to clean and preprocess observation CSVs (spiders, flies, etc.).
"""
from pathlib import Path
from typing import Optional, Union
import pandas as pd

# function to clean csv files 
# created to improve reusability and lessening code duplication in main analysis scripts
def clean_observation_csv(csv_path: Union[str, Path], 
                          start: pd.Timestamp, 
                          cutoff: pd.Timestamp, 
                          iconic_taxon: Optional[str] = None) -> pd.DataFrame:
    # creates a path object that will read all csv files passed through function
    # csv must be in string format
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path, dtype=str)

    # making sure the columns ('taxon_name' and 'observed_on') exists within the dataframe
    if iconic_taxon is not None:
        if "iconic_taxon_name" not in df.columns:
            raise KeyError(f"'iconic_taxon_name' column not found in {csv_path.name}" 
                           "but iconic_taxon filter was provided.")
        df = df[df["iconic_taxon_name"] == iconic_taxon].copy()

    if "observed_on" not in df.columns:
        raise KeyError(f"'observed_on' column not found in {csv_path.name}.")
    
    df['observed_on'] = pd.to_datetime(df["observed_on"], errors="coerce")
    df   = df.dropna(subset=["observed_on"])

    # making sure that we restrict the date range to a certain window for graph creation
    df = df[
        (df["observed_on"] >= start) & (df["observed_on"] <= cutoff)
    ].copy()

    # create year, month, and month-start date columns for future merging of dataframes
    df['year'] = df['observed_on'].dt.year
    df['month'] = df['observed_on'].dt.month
    df['date_month'] = df['observed_on'].values.astype('datetime64[M]')

    return df