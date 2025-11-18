# data_cleaning.py
"""
This module provides functions to clean and preprocess observation CSVs (spiders, flies, etc.).
You can import these functions in your analysis scripts for different taxa.
"""
import pandas as pd
from pathlib import Path

def clean_observation_csv(csv_path, start, cutoff, iconic_taxon=None):
    """
    Reads and cleans an observation CSV (e.g., spiders or flies).
    Filters by date, parses dates, and optionally filters by iconic_taxon_name.
    Returns a cleaned DataFrame with year, month, and date_month columns.
    """
    df = pd.read_csv(csv_path, dtype=str)
    if iconic_taxon:
        df = df[df["iconic_taxon_name"] == iconic_taxon].copy()
    df["observed_on"] = pd.to_datetime(df["observed_on"], errors="coerce")
    df = df.dropna(subset=["observed_on"])
    df = df[(df["observed_on"] >= start) & (df["observed_on"] <= cutoff)].copy()
    df["year"] = df["observed_on"].dt.year
    df["month"] = df["observed_on"].dt.month
    df["date_month"] = df["observed_on"].values.astype("datetime64[M]")
    return df
