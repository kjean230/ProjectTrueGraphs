# plotting_file.py

from typing import Optional, Sequence

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from data_aggregation import add_season_column


# ----------------------------------------------------------------------
# 1. Dual-axis time series: spiders, flies (left), AQI (right)
# ----------------------------------------------------------------------

def plot_abundance_aqi_time_series(
    df: pd.DataFrame,
    date_col: str = "date_month",
    spider_col: str = "spider_count",
    fly_col: str = "fly_count",
    aqi_col: str = "aqi_mean",
    x_label: str = "Month",
    left_y_label: str = "Monthly Arthropod Counts",
    right_y_label: str = "Mean AQI",
    title: str = "Spiders & Flies vs AQI Over Time",
    figsize: tuple[int, int] = (10, 6),
    output_filename: Optional[str] = None,
    smooth_window: Optional[int] = None,  # e.g. 3 for 3-month rolling mean
) -> None:
    """
    Time series with:
    - X: date
    - Left Y: spiders and flies
    - Right Y: AQI

    If smooth_window is provided, apply a centered rolling mean to each series.
    """

    subset_cols = [date_col, spider_col, fly_col, aqi_col]
    df_plot = df.dropna(subset=subset_cols).copy()
    if df_plot.empty:
        print("There's no data available to plot.")
        return

    df_plot = df_plot.sort_values(date_col)

    if smooth_window is not None and smooth_window > 1:
        for col in (spider_col, fly_col, aqi_col):
            df_plot[col] = (
                df_plot[col]
                .rolling(window=smooth_window, center=True, min_periods=1)
                .mean()
            )

    fig, ax1 = plt.subplots(figsize=figsize)

    # left axis: spiders & flies
    line_spider, = ax1.plot(
        df_plot[date_col],
        df_plot[spider_col],
        marker="o",
        linestyle="-",
        label="Spiders",
    )
    line_fly, = ax1.plot(
        df_plot[date_col],
        df_plot[fly_col],
        marker="o",
        linestyle="-",
        label="Flies",
    )
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(left_y_label)

    # right axis: AQI
    ax2 = ax1.twinx()
    line_aqi, = ax2.plot(
        df_plot[date_col],
        df_plot[aqi_col],
        linestyle="--",
        label="AQI",
    )
    ax2.set_ylabel(right_y_label)

    ax1.set_title(title)

    # combined legend
    lines = [line_spider, line_fly, line_aqi]
    labels = [ln.get_label() for ln in lines]
    ax1.legend(lines, labels, loc="upper left")

    fig.tight_layout()
    if output_filename:
        fig.savefig(output_filename, dpi=300, bbox_inches="tight")
    plt.show()


# ----------------------------------------------------------------------
# 2. Scatter: spiders & flies vs AQI, colored by year or season
# ----------------------------------------------------------------------

def _ensure_season_column_local(
    df: pd.DataFrame,
    month_col: str = "month",
    season_col: str = "season",
) -> pd.DataFrame:
    """
    Wrapper to ensure a 'season' column exists.
    Uses project's add_season_column logic.
    """
    if season_col in df.columns:
        return df
    if month_col not in df.columns:
        raise KeyError(
            f"DataFrame is missing '{season_col}' and '{month_col}', "
            "so seasons cannot be derived."
        )
    return add_season_column(df, month_col=month_col, season_col=season_col)


def plot_scatter_spiders_flies_colored(
    df: pd.DataFrame,
    x_col: str = "aqi_mean",
    spider_col: str = "spider_count",
    fly_col: str = "fly_count",
    color_by: str = "year",  # "year" or "season"
    x_label: str = "Air Quality Index (AQI)",
    y_label: str = "Monthly Arthropod Counts",
    title: str = "Spider & Fly Counts vs AQI",
    figsize: tuple[int, int] = (10, 6),
    output_filename: Optional[str] = None,
) -> None:
    """
    Scatter of spiders and flies vs the same x variable (e.g. AQI) on one plot.

    Species are separated by marker shape.
    Color encodes either year (continuous) or season (discrete).
    """

    if color_by not in ("year", "season"):
        raise ValueError("color_by must be 'year' or 'season'.")

    df_plot = df.copy()

    if color_by == "season":
        df_plot = _ensure_season_column_local(df_plot)

    subset_cols = [x_col, spider_col, fly_col]
    if color_by == "year":
        subset_cols.append("year")
    else:
        subset_cols.append("season")

    df_plot = df_plot.dropna(subset=subset_cols)
    if df_plot.empty:
        print("There's no data available to plot.")
        return

    # numeric conversion
    for col in (x_col, spider_col, fly_col):
        df_plot[col] = pd.to_numeric(df_plot[col], errors="coerce")
    df_plot = df_plot.dropna(subset=[x_col, spider_col, fly_col])
    if df_plot.empty:
        print("There's no data available to plot after numeric conversion.")
        return

    x = df_plot[x_col].values
    y_spiders = df_plot[spider_col].values
    y_flies = df_plot[fly_col].values

    fig, ax = plt.subplots(figsize=figsize)

    if color_by == "year":
        years = df_plot["year"].astype(int).values
        unique_years = np.unique(years)
        norm = plt.Normalize(vmin=unique_years.min(), vmax=unique_years.max())
        cmap = plt.cm.viridis
        colors = cmap(norm(years))

        ax.scatter(x, y_spiders, c=colors, marker="o", alpha=0.8, label="Spiders")
        ax.scatter(x, y_flies, c=colors, marker="x", alpha=0.8, label="Flies")

        cbar = fig.colorbar(
            plt.cm.ScalarMappable(norm=norm, cmap=cmap),
            ax=ax,
            label="Year",
        )

        handles_species = [
            plt.Line2D([], [], marker="o", linestyle="none", label="Spiders"),
            plt.Line2D([], [], marker="x", linestyle="none", label="Flies"),
        ]
        ax.legend(handles=handles_species, title="Species", loc="upper left")

    else:  # color_by == "season"
        seasons = df_plot["season"].astype(str)
        season_order = ["Winter", "Summer", "Fall"]
        colors_map = {
            "Winter": "tab:blue",
            "Summer": "tab:orange",
            "Fall": "tab:green",
        }

        for season in season_order:
            mask = seasons == season
            if not mask.any():
                continue
            color = colors_map.get(season, "grey")

            ax.scatter(
                x[mask],
                y_spiders[mask],
                color=color,
                marker="o",
                alpha=0.8,
                label=f"Spiders ({season})",
            )
            ax.scatter(
                x[mask],
                y_flies[mask],
                color=color,
                marker="x",
                alpha=0.8,
                label=f"Flies ({season})",
            )

        # two-level legend: species + season
        handles_species = [
            plt.Line2D([], [], marker="o", linestyle="none", color="black", label="Spiders"),
            plt.Line2D([], [], marker="x", linestyle="none", color="black", label="Flies"),
        ]
        legend1 = ax.legend(handles=handles_species, title="Species", loc="upper left")

        handles_season = [
            plt.Line2D([], [], marker="o", linestyle="none",
                       color=colors_map["Winter"], label="Winter"),
            plt.Line2D([], [], marker="o", linestyle="none",
                       color=colors_map["Summer"], label="Summer"),
            plt.Line2D([], [], marker="o", linestyle="none",
                       color=colors_map["Fall"], label="Fall"),
        ]
        legend2 = ax.legend(handles=handles_season, title="Season", loc="upper right")
        ax.add_artist(legend1)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    fig.tight_layout()
    if output_filename:
        fig.savefig(output_filename, dpi=300, bbox_inches="tight")
    plt.show()


# ----------------------------------------------------------------------
# 3. Seasonal grouped bar (spiders & flies) + AQI line
# ----------------------------------------------------------------------

def plot_seasonal_grouped_bar_with_aqi(
    df: pd.DataFrame,
    year_col: str = "year",
    month_col: str = "month",
    spider_col: str = "spider_count",
    fly_col: str = "fly_count",
    aqi_col: str = "aqi_mean",
    season_col: str = "season",
    x_label: str = "Year-Season",
    left_y_label: str = "Mean Arthropod Counts",
    right_y_label: str = "Mean AQI",
    title: str = "Seasonal Arthropod Counts and AQI",
    figsize: tuple[int, int] = (10, 6),
    output_filename: Optional[str] = None,
) -> None:
    """
    Group by (year, season), then:
    - Left axis: grouped bars for mean spider and fly counts.
    - Right axis: line for mean AQI.
    """

    subset_cols = [year_col, month_col, spider_col, fly_col, aqi_col]
    df_plot = df.dropna(subset=subset_cols).copy()
    if df_plot.empty:
        print("There's no data available to plot.")
        return

    df_plot = _ensure_season_column_local(df_plot, month_col=month_col, season_col=season_col)

    grouped = (
        df_plot
        .groupby([year_col, season_col])[[spider_col, fly_col, aqi_col]]
        .mean()
        .reset_index()
        .sort_values([year_col, season_col])
    )
    if grouped.empty:
        print("No seasonal data after grouping.")
        return

    labels = grouped.apply(
        lambda row: f"{int(row[year_col])}-{row[season_col][0]}", axis=1
    )  # e.g. "2018-W", "2018-S"

    x = np.arange(len(grouped))
    width = 0.35

    fig, ax1 = plt.subplots(figsize=figsize)

    bar_spider = ax1.bar(
        x - width / 2,
        grouped[spider_col],
        width=width,
        label="Spiders",
    )
    bar_fly = ax1.bar(
        x + width / 2,
        grouped[fly_col],
        width=width,
        label="Flies",
    )

    ax1.set_xlabel(x_label)
    ax1.set_ylabel(left_y_label)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=45, ha="right")

    ax2 = ax1.twinx()
    line_aqi, = ax2.plot(
        x,
        grouped[aqi_col],
        marker="o",
        linestyle="--",
        label="AQI",
    )
    ax2.set_ylabel(right_y_label)

    ax1.set_title(title)

    # combined legend
    handles = [bar_spider, bar_fly, line_aqi]
    labels_legend = ["Spiders", "Flies", "AQI"]
    ax1.legend(handles, labels_legend, loc="upper left")

    fig.tight_layout()
    if output_filename:
        fig.savefig(output_filename, dpi=300, bbox_inches="tight")
    plt.show()


# ----------------------------------------------------------------------
# 4. AQI-binned bar chart (low/med/high AQI vs counts)
# ----------------------------------------------------------------------

def plot_aqi_binned_bar(
    df: pd.DataFrame,
    aqi_col: str = "aqi_mean",
    spider_col: str = "spider_count",
    fly_col: str = "fly_count",
    bins: Optional[Sequence[float]] = None,
    bin_labels: Optional[Sequence[str]] = None,
    x_label: str = "AQI bin",
    y_label: str = "Mean Arthropod Counts",
    title: str = "Arthropod Counts by AQI Bin",
    figsize: tuple[int, int] = (8, 5),
    output_filename: Optional[str] = None,
) -> None:
    """
    Bin AQI and plot mean spider/fly counts in each AQI bin.

    If bins are not provided, uses tertiles (q=3) of AQI as default bins.
    """

    subset_cols = [aqi_col, spider_col, fly_col]
    df_plot = df.dropna(subset=subset_cols).copy()
    if df_plot.empty:
        print("There's no data available to plot.")
        return

    for col in (aqi_col, spider_col, fly_col):
        df_plot[col] = pd.to_numeric(df_plot[col], errors="coerce")
    df_plot = df_plot.dropna(subset=[aqi_col, spider_col, fly_col])
    if df_plot.empty:
        print("There's no data available to plot after numeric conversion.")
        return

    if bins is not None:
        # user-specified bins
        df_plot["aqi_bin"] = pd.cut(
            df_plot[aqi_col],
            bins=bins,
            labels=bin_labels,
            include_lowest=True,
        )
    else:
        # automatic tertiles
        df_plot["aqi_bin"] = pd.qcut(
            df_plot[aqi_col],
            q=3,
            duplicates="drop",
        )

    grouped = (
        df_plot
        .groupby("aqi_bin")[[spider_col, fly_col]]
        .mean()
        .reset_index()
    )
    if grouped.empty:
        print("No data after AQI binning.")
        return

    x = np.arange(len(grouped))
    width = 0.35

    fig, ax = plt.subplots(figsize=figsize)

    bar_spider = ax.bar(
        x - width / 2,
        grouped[spider_col],
        width=width,
        label="Spiders",
    )
    bar_fly = ax.bar(
        x + width / 2,
        grouped[fly_col],
        width=width,
        label="Flies",
    )

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(grouped["aqi_bin"].astype(str), rotation=45, ha="right")
    ax.legend()

    fig.tight_layout()
    if output_filename:
        fig.savefig(output_filename, dpi=300, bbox_inches="tight")
    plt.show()
