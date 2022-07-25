from helpers.analyses import get_percent_count_groupby
from helpers.transformations import (
    add_columns_to_df,
    clean_dataframe,
    remove_outliers,
)
from helpers.visualisations import (
    create_bar_chart,
    create_box_plot,
    create_pie_chart,
    visualize_accomodations_on_map,
)
import os
import pandas as pd


DEFAULT_VIZ_OUT_DIR = os.path.join(".", "visualizations")
DATA_SOURCE_BASE_URL = "http://data.insideairbnb.com/the-netherlands/north-holland/amsterdam/2022-03-08/data/"


def write_visualisations_to_local_dir(df=None, directory=None):
    """Creates and writes visualisation for the host analysis to a local directory."""

    directory = directory if directory else DEFAULT_VIZ_OUT_DIR

    # Create directory for visualisation if it doesn't exist already
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Get and clean data
    df = (
        df
        if df
        else pd.read_csv(
            os.path.join(DATA_SOURCE_BASE_URL, "listings.csv.gz"), compression="gzip"
        )
    )
    clean_dataframe(df)
    add_columns_to_df(df)

    # Create map
    visualize_accomodations_on_map(df, fig_name="map", viz_dir=directory)

    # Pie chart percent superhost listings
    create_pie_chart(
        df,
        "host_type",
        title="Percentage of listings by host type",
        legend_title="Is Superhost",
        viz_dir=directory,
    )

    # Bar charts
    for metric in [
        "host_response_time",
        "host_identity_verified",
        "neighbourhood_cleansed",
    ]:
        create_bar_chart(
            get_percent_count_groupby(df, ["host_type", metric]),
            x="percent",
            y=metric,
            color="host_type",
            orientation="h",
            fig_name=metric,
            width=600,
            height=400,
            viz_dir=directory,
        )

    # Box plots
    for metric in [
        "availability_365",
        "host_acceptance_rate",
        "reviews_per_month",
        "host_response_rate",
        "description_length",
        "host_about_length",
        "neighborhood_overview_length",
        "number_of_amenities",
        "number_of_host_verifications",
        "review_scores_rating",
    ]:
        create_box_plot(
            remove_outliers(df.dropna(subset=[metric]), metric),
            x="host_type",
            y=metric,
            fig_name=metric,
            viz_dir=directory,
        )


if __name__ == "__main__":
    write_visualisations_to_local_dir(
        df=None,  # Upload own dataframe else it will be pulled automatically
        directory=None,  # Specify own directory or leave blank for default
    )
