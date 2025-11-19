#plotting_file.py

# file for making plots and graphs for analysis
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

# scatter plot method based off information from dataframes
def plot_scatter_by_year(
        df: pd.DataFrame,
        x_col: str,
        y_col: str, 
        year_col: str = "year",
        x_label: str = "",
        y_label: str = "",
        title: str = "",
        figsize = (10, 6),
) -> None:
    # removes any rows with null values within specific columns
    df_plot = df.dropna(subset=[x_col, y_col, year_col])
    fig, ax = plt.subplots(figure=figsize)

    for year, group in df_plot.groupby(year_col):
        group_sorted = group.sort_values(x_col)
        ax.plot(
            group_sorted(x_col),
            group_sorted(y_col),
            marker="o",
            linestyle="-",
            label=str(year),
        )
    
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend(title=year_col.capitalize())

    fig.tight_layout()
    plt.show()
    
# plotting a time series graph based off dataframes
def plot_time_series(
        df: pd.DataFrame,
        x_col: str,
        y1_col: str,
        y2_col: str | None = None,
        x_label: str = "",
        y1_label: str = "",
        y2_label: str = "",
        title: str = "",
        figsize = (10, 6),      
) -> None:
    subset_cols = [x_col, y1_col]
    df_plot = df.dropna(subset=subset_cols).copy()
    if df_plot.empty:
        print("There's no data avaiable to plot.")
        return
    
    df_plot = df.sort_values(x_col)
    fig, ax1 = plt.subplots(figure=figsize)
    ax1.plot(
        df_plot[x_col],
        df_plot[y1_col],
        marker="o",
        linestyle="-",
        label=y1_col,
    )
    ax1.set_xlabel(x_label if x_label else x_col)
    ax1.set_ylabel(y1_label if y1_label else y1_col)

    ax2 = None
    if y2_col is not None:
        ax2 = ax1.twinx()
        ax2.plot(
            df_plot[x_col],
            df_plot[y2_col],
            marker="o",
            linestyle="--",
            label=y2_col,
        )
        ax2.set_ylabel(y2_label if y2_label else y2_col)
    
    # title of the graph 
    ax1.set_title(title if title else f"{y1_col} over time")

    if y2_col is not None:
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    else:
        ax1.legend(loc="upper left")

    fig.tight_layout()
    plt.show()
