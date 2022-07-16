import ast
import warnings
from geopy import distance
import os
import itertools
import math
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import folium


DEFAULT_FIG_HEIGHT = 400
DEFAULT_FIG_WIDTH = 600
DEFAULT_VIZ_OUT_DIR = os.path.join(".", "visualizations")
DEFAULT_SUPER_HOST_COLOR = "#C80000"
DEFAULT_REGULAR_HOST_COLOR = "#464646"
DEFAULT_COLOR_MAPPING = {
    True: DEFAULT_SUPER_HOST_COLOR,
    False: DEFAULT_REGULAR_HOST_COLOR,
}


def get_colors():
    """Returns a list of RGB colors"""
    colors = list(px.colors.qualitative.Set2)
    colors.extend(px.colors.qualitative.Pastel2)
    colors.extend(px.colors.qualitative.Dark2)
    colors.extend(px.colors.qualitative.Set3)
    colors.extend(px.colors.qualitative.Pastel)
    return colors


def get_distance_in_km(lat1, lon1, lat2, lon2):
    """Returns the geodesic distance between two coordinates described by latitude and longitude."""
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return distance.distance(point1, point2).km


def calculate_distance_to_amsterdam_centrum(lat, lon):
    """Returns the geodesic distance between the centre of Amsgterdam and a given coordinate."""
    ams_centrum_lat = 52.3676
    ams_centrum_lon = 4.9041
    return get_distance_in_km(lat, lon, ams_centrum_lat, ams_centrum_lon)


def print_percent_na_per_col(df):
    """Prints the percentage of missing values per column in a pandas.DataFrame"""
    print((df.isna().sum() / df.shape[0]).sort_values(ascending=False))


def drop_na_columns(df, percentage_threshold):
    """Removes columns from a pandas.DataFrame with missing values equla or higher to threshold"""
    absolute_treshold = int(df.shape[1] * (1 - percentage_threshold))
    cols_before_dropping = set(df.columns)
    df.dropna(axis=1, thresh=absolute_treshold, inplace=True)
    dropped_cols = cols_before_dropping.difference(set(df.columns))
    if len(dropped_cols) > 0:
        print(
            f"The following columns with {percentage_threshold * 100}% or more missing values were dropped:"
        )
        print(*dropped_cols, sep="\n")
    else:
        print("No columns were dropped.")
    print("\n")


def print_duplicates_summary(df, col_dtypes=["int64", "float64"]):
    """Print the number of duplicate values in each column of given dtype of a pandas.DataFrame"""
    print("Number of duplicated values in df:", df.duplicated().sum())
    numeric_cols = [c for c in df.select_dtypes(include=col_dtypes).columns]
    output = pd.Series(dtype="object")
    for c in numeric_cols:
        output = pd.concat([output, pd.Series(data={c: df.duplicated(c).sum()})])
    print(output.sort_values(ascending=False))


def create_subplots(df, plot_type="histogram", exclude_cols=None):
    """Takes a pandas.DataFrame and returns plotly sublots with histograms or boxplots for numeric columns."""
    numeric_cols = [c for c in df.select_dtypes(include=["int64", "float64"]).columns]
    if exclude_cols:
        numeric_cols = [c for c in numeric_cols if c not in exclude_cols]

    subplot_dim = {
        "rows": {
            "histogram": math.ceil(len(numeric_cols) / 2),
            "boxplot": math.ceil(len(numeric_cols) / 4),
        },
        "cols": {"histogram": 2, "boxplot": 4},
        "height": 300 * math.ceil(len(numeric_cols) / 2),
        "width": 1400,
    }
    fig = make_subplots(
        rows=subplot_dim["rows"][plot_type],
        cols=subplot_dim["cols"][plot_type],
        subplot_titles=numeric_cols,
    )
    rows_cols = itertools.product(
        range(1, subplot_dim["rows"][plot_type] + 1),
        range(1, subplot_dim["cols"][plot_type] + 1),
    )
    for c, row_col in zip(numeric_cols, rows_cols):
        if plot_type == "histogram":
            fig.add_trace(go.Histogram(x=df[c], name=c), row=row_col[0], col=row_col[1])
        elif plot_type == "boxplot":
            fig.add_trace(go.Box(y=df[c], name=c), row=row_col[0], col=row_col[1])

    fig.update_layout(
        showlegend=False,
        height=subplot_dim["height"],
        width=subplot_dim["width"],
        title_text=plot_type.capitalize(),
    )
    return fig


def create_histogramms_boxplots(df, exclude_cols=None):
    """Takes a pandas.DataFrame and returns plotly sublots with histograms or boxplots for numeric columns."""
    colors = get_colors()
    numeric_cols = [c for c in df.select_dtypes(include=["int64", "float64"]).columns]
    if exclude_cols:
        numeric_cols = [c for c in numeric_cols if c not in exclude_cols]

    fig = make_subplots(rows=len(numeric_cols), cols=2, column_widths=[0.8, 0.2])
    for i, c in enumerate(numeric_cols):
        fig.add_trace(
            go.Histogram(x=df[c], name=c, marker_color=colors[i]), row=i + 1, col=1
        )
        fig.add_trace(go.Box(y=df[c], name=c, marker_color=colors[i]), row=i + 1, col=2)

    fig.update_layout(showlegend=False, height=400 * len(numeric_cols), width=1600)
    return fig


def drop_columns_containing_keyword(df, keyword):
    """Drops columns from a pandas.DataFrame containing the specified keyword"""
    cols_to_drop = [c for c in df.columns if keyword in c]
    print(f"Dropping the following columns containing '{keyword}':")
    print(*cols_to_drop, sep="  \n")
    df.drop(cols_to_drop, axis=1, inplace=True)
    print("\n")


def clean_dataframe(df):
    """Takes a pandas.DataFrame and performs a series of data cleaning steps."""
    # Drop columns containing '_url' or 'scrape' in their name
    drop_columns_containing_keyword(df, "_url")
    drop_columns_containing_keyword(df, "scrape")

    # Extract numeric price
    df["price_dollar"] = (
        df.price.str.replace(",", "", regex=False).str[1:].astype("float")
    )

    # Fix data types
    df["id"] = df["id"].astype("str")
    df["host_id"] = df["host_id"].astype("str")
    df["last_review"] = pd.to_datetime(df["last_review"])
    df["amenities"] = df["amenities"].apply(lambda x: ast.literal_eval(x))
    df["host_response_rate"] = (
        df["host_response_rate"].str.replace("%", "").astype("float") / 100
    )
    df["host_acceptance_rate"] = (
        df["host_acceptance_rate"].str.replace("%", "").astype("float") / 100
    )

    # Replace t and f strings with boolean values
    for col in df.columns:
        if len(df[col].value_counts()) < 5:
            if set(df[col].unique()) == {"f", "t"}:
                df[col].replace(["t", "f"], [True, False], inplace=True)

    # Remove listings with price equal to 0 (or below)
    df = df.loc[df["price_dollar"] > 0].reset_index(drop=True)

    # Remove columns with 90% or more missing values
    drop_na_columns(df, 0.9)

    # Remove outlier with too high price
    df = df.loc[df["price_dollar"] < 8000].reset_index(drop=True)

    # Drop other not needed columns
    df.drop(
        [
            "neighbourhood",
            "price",
            "minimum_nights",
            "minimum_minimum_nights",
            "minimum_maximum_nights",
            "maximum_nights",
            "maximum_maximum_nights",
            "maximum_minimum_nights",
            "has_availability",
            "availability_30",
            "availability_60",
            "availability_90",
        ],
        axis=1,
        inplace=True,
    )


def get_percent_count_groupby(df, groupby_cols=["host_is_superhost"]):
    return (
        df.groupby(groupby_cols)
        .agg(percent=("id", "count"))
        .groupby(level=0)
        .apply(lambda x: 100 * x / x.sum())
    ).reset_index()


def visualize_accomodations_on_map(df, fig_name=None):
    """ ."""
    m = folium.Map(
        location=[df["latitude"].median(), df["longitude"].median()], zoom_start=12
    )

    for lat, lon, is_sh in zip(
        df["latitude"], df["longitude"], df["host_is_superhost"]
    ):
        folium.Circle(
            radius=60,
            location=[lat, lon],
            stroke=True,
            color=DEFAULT_COLOR_MAPPING[is_sh],
            weight=1,
            opacity=0.2,
            fill=True,
            tooltip=is_sh,
        ).add_to(m)

    fig_name = fig_name if fig_name else "box"
    m.save(os.path.join(DEFAULT_VIZ_OUT_DIR, f"{fig_name}.html"))

    return m


def update_fig_layout(
    fig,
    title=None,
    height=None,
    width=None,
    xaxis_title=None,
    yaxis_title=None,
    showlegend=False,
    legend_title=None,
):
    fig.update_layout(
        title_text=title,
        plot_bgcolor="#FFFFFF",
        height=height if height else DEFAULT_FIG_HEIGHT,
        width=width if width else DEFAULT_FIG_WIDTH,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        showlegend=showlegend,
        legend=dict(title=legend_title),
    )


def create_bar_chart(
    df,
    x,
    y,
    color=None,
    orientation="v",
    barmode="group",
    opacity=1,
    showlegend=True,
    height=None,
    width=None,
    title=None,
    legend_title=None,
    xaxis_title=None,
    yaxis_title=None,
    fig_name=None,
):
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        barmode=barmode,
        opacity=opacity,
        orientation=orientation,
        color_discrete_map=DEFAULT_COLOR_MAPPING,
    )

    update_fig_layout(
        fig, title, height, width, xaxis_title, yaxis_title, showlegend, legend_title,
    )
    fig_name = fig_name if fig_name else "bar"
    fig.write_html(os.path.join(DEFAULT_VIZ_OUT_DIR, f"{fig_name}.html"))

    return fig


def create_box_plot(
    df,
    x,
    y,
    color=None,
    showlegend=True,
    height=None,
    width=None,
    title=None,
    legend_title=None,
    xaxis_title=None,
    yaxis_title=None,
    fig_name=None,
):

    fig = px.box(
        df,
        x=x,
        y=y,
        color=color if color else x,
        color_discrete_map=DEFAULT_COLOR_MAPPING,
    )

    update_fig_layout(
        fig, title, height, width, xaxis_title, yaxis_title, showlegend, legend_title,
    )

    fig_name = fig_name if fig_name else "box"
    fig.write_html(os.path.join(DEFAULT_VIZ_OUT_DIR, f"{fig_name}.html"))

    return fig


def create_pie_chart(
    df,
    names,
    color=None,
    title=None,
    height=None,
    width=None,
    showlegend=True,
    legend_title=None,
    fig_name=None,
):
    fig = px.pie(
        df,
        names=names,
        hole=0.5,
        color=color if color else names,
        color_discrete_map=DEFAULT_COLOR_MAPPING,
    )
    fig.update_traces(textinfo="percent")
    fig.add_annotation(text=f"{df.shape[0]} Listings", showarrow=False)
    update_fig_layout(
        fig,
        title=title,
        height=height,
        width=width,
        showlegend=showlegend,
        legend_title=legend_title,
    )
    fig_name = fig_name if fig_name else "pie"
    fig.write_html(os.path.join(DEFAULT_VIZ_OUT_DIR, f"{fig_name}.html"))

    return fig


def print_metric_mean_by_host_type(df, column_name):
    print(
        f"Average {column_name} superhosts:",
        round(df.loc[df["host_is_superhost"]][column_name].mean(), 2),
    )
    print(
        f"Average {column_name} regular hosts:",
        round(df.loc[~df["host_is_superhost"]][column_name].mean(), 2),
    )


def remove_outliers(df, metric, sd_threshold=2, warning_treshold=0.05):
    avg = df[metric].mean()
    sd = df[metric].std()
    lower_cutoff = avg - sd * sd_threshold
    upper_cutoff = avg + sd * sd_threshold
    df_out = df.loc[(df[metric] <= upper_cutoff) & (df[metric] >= lower_cutoff)]
    values_removed = df.shape[0] - df_out.shape[0]
    if values_removed / df.shape[0] > warning_treshold:
        warnings.warn(
            f"More than {warning_treshold*100}% of values removed ({values_removed})!"
        )
    return df_out
