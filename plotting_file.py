# plotting_file.py

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt


def plot_scatter_by_year(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        year_col: str = "year",
        x_label: str = "",
        y_label: str = "",
        title: str = "",
        figsize=(10, 6),
        output_filename: Optional[str] = None,
) -> None:
    """
    Scatter/line plot of y vs x, colored by year.
    """

    df_plot = df.dropna(subset=[x_col, y_col, year_col])
    if df_plot.empty:
        print("There's no data available to plot.")
        return

    fig, ax = plt.subplots(figsize=figsize)

    for year, group in df_plot.groupby(year_col):
        group_sorted = group.sort_values(x_col)
        ax.plot(
            group_sorted[x_col],
            group_sorted[y_col],
            marker="o",
            linestyle="-",
            label=str(year),
        )

    ax.set_xlabel(x_label if x_label else x_col)
    ax.set_ylabel(y_label if y_label else y_col)
    ax.set_title(title)
    ax.legend(title=year_col.capitalize())

    fig.tight_layout()

    if output_filename:
        fig.savefig(output_filename, dpi=300, bbox_inches="tight")

    plt.show()


def plot_time_series(
        df: pd.DataFrame,
        date_col: str,
        y_col: str,
        y2_col: Optional[str] = None,
        x_label: str = "",
        y_label: str = "",
        y2_label: str = "",
        title: str = "",
        figsize=(10, 6),
        output_filename: Optional[str] = None,
) -> None:
    """
    Time series plot:
    - y_col vs date_col on primary y-axis
    - optional y2_col vs date_col on secondary y-axis
    """

    subset_cols = [date_col, y_col]
    if y2_col is not None:
        subset_cols.append(y2_col)

    df_plot = df.dropna(subset=subset_cols).copy()
    if df_plot.empty:
        print("There's no data available to plot.")
        return

    df_plot = df_plot.sort_values(date_col)

    fig, ax1 = plt.subplots(figsize=figsize)

    # primary series
    ax1.plot(
        df_plot[date_col],
        df_plot[y_col],
        marker="o",
        linestyle="-",
        label=y_col,
    )
    ax1.set_xlabel(x_label if x_label else date_col)
    ax1.set_ylabel(y_label if y_label else y_col)

    ax2 = None
    if y2_col is not None:
        ax2 = ax1.twinx()
        ax2.plot(
            df_plot[date_col],
            df_plot[y2_col],
            marker="o",
            linestyle="--",
            label=y2_col,
        )
        ax2.set_ylabel(y2_label if y2_label else y2_col)

    ax1.set_title(title if title else f"{y_col} over time")

    if y2_col is not None:
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    else:
        ax1.legend(loc="upper left")

    fig.tight_layout()

    if output_filename:
        fig.savefig(output_filename, dpi=300, bbox_inches="tight")

    plt.show()
