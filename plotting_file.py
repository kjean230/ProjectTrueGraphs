# plotting_file.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional


def _ensure_season_column(df: pd.DataFrame,
                          month_col: str = "month",
                          season_col: str = "season") -> pd.DataFrame:
    """Add a 'season' column if missing, based on month."""
    if season_col in df.columns:
        return df

    if month_col not in df.columns:
        raise KeyError(
            f"DataFrame is missing '{season_col}' and '{month_col}', "
            "so seasons cannot be derived."
        )

    def month_to_season(m: int) -> str:
        if m in [1, 2, 3]:
            return "Winter"
        elif m in [4, 5, 6, 7, 8]:
            return "Summer"
        elif m in [9, 10, 11, 12]:
            return "Fall"
        else:
            raise ValueError(f"Month out of range: {m}")

    df = df.copy()
    df[season_col] = df[month_col].astype(int).apply(month_to_season)
    return df


def plot_scatter_spiders_flies_colored(
        df: pd.DataFrame,
        x_col: str,                 # e.g. "aqi_mean"
        spider_col: str,           # e.g. "spider_count"
        fly_col: str,              # e.g. "fly_count"
        color_by: str = "year",    # "year" or "season"
        x_label: str = "",
        y_label: str = "",
        title: str = "",
        figsize=(10, 6),
        output_filename: Optional[str] = None,
) -> None:
    """
    Scatter of spiders and flies vs the same x variable (e.g. AQI) on one plot.

    - Species are separated by marker shape.
    - Color encodes either year (continuous colorbar) or season (discrete colors).
    """

    # minimal required columns
    subset_cols = [x_col, spider_col, fly_col]
    if color_by == "year":
        subset_cols.append("year")
    elif color_by == "season":
        # ensure we have a season column (derive from month if needed)
        df = _ensure_season_column(df)
        subset_cols.append("season")
    else:
        raise ValueError("color_by must be 'year' or 'season'.")

    df_plot = df.dropna(subset=subset_cols).copy()
    if df_plot.empty:
        print("There's no data available to plot.")
        return

    # numeric conversions
    df_plot[x_col] = pd.to_numeric(df_plot[x_col], errors="coerce")
    df_plot[spider_col] = pd.to_numeric(df_plot[spider_col], errors="coerce")
    df_plot[fly_col] = pd.to_numeric(df_plot[fly_col], errors="coerce")
    df_plot = df_plot.dropna(subset=[x_col, spider_col, fly_col])
    if df_plot.empty:
        print("There's no data available to plot after numeric conversion.")
        return

    fig, ax = plt.subplots(figsize=figsize)

    # base arrays
    x = df_plot[x_col].values
    y_spiders = df_plot[spider_col].values
    y_flies = df_plot[fly_col].values

    # --- color encoding ---
    if color_by == "year":
        years = df_plot["year"].astype(int).values
        unique_years = np.unique(years)

        # continuous colormap over years
        norm = plt.Normalize(vmin=unique_years.min(), vmax=unique_years.max())
        cmap = plt.cm.viridis
        colors = cmap(norm(years))

        # spiders
        sc_sp = ax.scatter(
            x, y_spiders,
            c=colors,
            marker="o",
            alpha=0.8,
            label="Spiders",
        )

        # flies
        sc_fl = ax.scatter(
            x, y_flies,
            c=colors,
            marker="x",
            alpha=0.8,
            label="Flies",
        )

        # colorbar for year
        cbar = fig.colorbar(
            plt.cm.ScalarMappable(norm=norm, cmap=cmap),
            ax=ax,
            label="Year",
        )

        # species legend (shapes)
        handles_species = [
            plt.Line2D([], [], marker="o", linestyle="none", label="Spiders"),
            plt.Line2D([], [], marker="x", linestyle="none", label="Flies"),
        ]
        ax.legend(handles=handles_species, title="Species", loc="upper left")

    elif color_by == "season":
        df_plot = _ensure_season_column(df_plot)
        seasons = df_plot["season"].astype(str)
        season_order = ["Winter", "Summer", "Fall"]
        colors_map = {
            "Winter": "tab:blue",
            "Summer": "tab:orange",
            "Fall": "tab:green",
        }

        # spiders and flies by season
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

        # build compact legend: separate species and seasons
        # species legend
        handles_species = [
            plt.Line2D([], [], marker="o", linestyle="none", color="black", label="Spiders"),
            plt.Line2D([], [], marker="x", linestyle="none", color="black", label="Flies"),
        ]
        legend1 = ax.legend(handles=handles_species, title="Species", loc="upper left")

        # seasons legend
        handles_season = [
            plt.Line2D([], [], marker="o", linestyle="none",
                       color=colors_map["Winter"], label="Winter"),
            plt.Line2D([], [], marker="o", linestyle="none",
                       color=colors_map["Summer"], label="Summer"),
            plt.Line2D([], [], marker="o", linestyle="none",
                       color=colors_map["Fall"], label="Fall"),
        ]
        legend2 = ax.legend(handles=handles_season, title="Season", loc="upper right")
        ax.add_artist(legend1)  # keep both legends

    # axis labels and title
    ax.set_xlabel(x_label if x_label else x_col)
    ax.set_ylabel(y_label if y_label else "Count")
    ax.set_title(title if title else f"{spider_col} and {fly_col} vs {x_col}")

    fig.tight_layout()
    if output_filename:
        fig.savefig(output_filename, dpi=300, bbox_inches="tight")
    plt.show()


# ======= time series plotting function ======= #
def plot_abundance_aqi_time_series(
        df: pd.DataFrame,
        date_col: str,
        spider_col: str,
        fly_col: str,
        aqi_col: str,
        x_label: str = "",
        left_y_label: str = "",
        right_y_label: str = "",
        title: str = "",
        figsize=(10, 6),
        output_filename: Optional[str] = None,
        smooth_window: Optional[int] = None,   # e.g. 3, 5 for moving average
) -> None:
    """
    Time series with:
    - Left Y: spider and fly abundance
    - Right Y: air quality (AQI)
    - X: date (months/years)

    If smooth_window is provided, apply a centered rolling mean to each series.
    """

    subset_cols = [date_col, spider_col, fly_col, aqi_col]
    df_plot = df.dropna(subset=subset_cols).copy()
    if df_plot.empty:
        print("There's no data available to plot.")
        return

    df_plot = df_plot.sort_values(date_col)

    # Optional smoothing: rolling mean
    if smooth_window is not None and smooth_window > 1:
        df_plot[spider_col] = (
            df_plot[spider_col]
            .rolling(window=smooth_window, center=True, min_periods=1)
            .mean()
        )
        df_plot[fly_col] = (
            df_plot[fly_col]
            .rolling(window=smooth_window, center=True, min_periods=1)
            .mean()
        )
        df_plot[aqi_col] = (
            df_plot[aqi_col]
            .rolling(window=smooth_window, center=True, min_periods=1)
            .mean()
        )

    fig, ax1 = plt.subplots(figsize=figsize)

    # Left y-axis: spiders & flies
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

    ax1.set_xlabel(x_label if x_label else date_col)
    ax1.set_ylabel(left_y_label if left_y_label else "Abundance")

    # Right y-axis: AQI
    ax2 = ax1.twinx()
    line_aqi, = ax2.plot(
        df_plot[date_col],
        df_plot[aqi_col],
        linestyle="--",
        label="AQI",
    )
    ax2.set_ylabel(right_y_label if right_y_label else "AQI")

    # Title
    ax1.set_title(
        title if title else "Arthropod abundance and AQI over time"
    )

    # Combined legend
    lines = [line_spider, line_fly, line_aqi]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper left")

    fig.tight_layout()

    if output_filename:
        fig.savefig(output_filename, dpi=300, bbox_inches="tight")

    plt.show()
