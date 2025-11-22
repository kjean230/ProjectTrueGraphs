# user_input_to_create_graph.py
# file to handle user input for creating graphs

import pandas as pd

from plotting_file import (
    plot_abundance_aqi_time_series,
    plot_scatter_spiders_flies_colored,
    plot_seasonal_grouped_bar_with_aqi,
    plot_aqi_binned_bar,
)


def create_graph_from_choice(choice: str, df_monthly: pd.DataFrame) -> None:
   # based on whatever the user wants, create the appropriate graph
   # choices include: time_series, scatter, seasonal_bar, aqi_bins
   # function to reduce clutter in main analysis script
   # easier debugging and future modifications

    choice_norm = choice.strip().lower()

    if choice_norm in {"time_series", "time series", "1"}:
        plot_abundance_aqi_time_series(
            df_monthly,
            date_col="date_month",
            spider_col="spider_count",
            fly_col="fly_count",
            aqi_col="aqi_mean",
            smooth_window=3,
            output_filename="time_series_spider_fly_aqi.png",
        )

    elif choice_norm in {"scatter", "scatter_season", "2"}:
        # scatter, colored by season
        plot_scatter_spiders_flies_colored(
            df_monthly,
            x_col="aqi_mean",
            spider_col="spider_count",
            fly_col="fly_count",
            color_by="season",  # or "year"
            output_filename="scatter_spider_fly_aqi_by_season.png",
        )

    elif choice_norm in {"seasonal_bar", "seasonal", "3"}:
        plot_seasonal_grouped_bar_with_aqi(
            df_monthly,
            year_col="year",
            month_col="month",
            spider_col="spider_count",
            fly_col="fly_count",
            aqi_col="aqi_mean",
            output_filename="seasonal_bar_spider_fly_aqi.png",
        )

    elif choice_norm in {"aqi_bins", "bins", "4"}:
        plot_aqi_binned_bar(
            df_monthly,
            aqi_col="aqi_mean",
            spider_col="spider_count",
            fly_col="fly_count",
            output_filename="aqi_binned_spider_fly.png",
        )

    else:
        print(
            "Unrecognized graph choice. "
            "Valid options: time_series, scatter, seasonal_bar, aqi_bins."
        )
