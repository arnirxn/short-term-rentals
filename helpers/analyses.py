from geopy import distance
import pandas as pd
from scipy.stats import ttest_ind


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


def print_duplicates_summary(df, col_dtypes=["int64", "float64"]):
    """Print the number of duplicate values in each column of given dtype of a pandas.DataFrame"""
    print("Number of duplicated values in df:", df.duplicated().sum())
    numeric_cols = [c for c in df.select_dtypes(include=col_dtypes).columns]
    output = pd.Series(dtype="object")
    for c in numeric_cols:
        output = pd.concat([output, pd.Series(data={c: df.duplicated(c).sum()})])
    print(output.sort_values(ascending=False))


def get_percent_count_groupby(df, groupby_cols=["host_is_superhost"]):
    """Returns a pandas.DataFrame with the the percentage count grouped by the given column."""
    return (
        df.groupby(groupby_cols)
        .agg(percent=("id", "count"))
        .groupby(level=0)
        .apply(lambda x: 100 * x / x.sum())
    ).reset_index()


def print_metric_mean_by_host_type(df, column_name):
    """Prints the average by host type for a given metric in a pandas.DataFrame."""
    print(
        f"Average {column_name} superhosts:",
        round(df.loc[df["host_is_superhost"]][column_name].mean(), 2),
    )
    print(
        f"Average {column_name} regular hosts:",
        round(df.loc[~df["host_is_superhost"]][column_name].mean(), 2),
    )


def run_ttest_independent(df1, df2, metric_col):
    """Performs an independent t-test and prints the significance of the test."""
    res = ttest_ind(df1[metric_col].dropna(), df2[metric_col].dropna())
    p_value = res.pvalue
    print(
        f"Significance of Independent T-Test comparing Superhosts and regular hosts on {metric_col}:"
    )
    if p_value < 0.001:
        print(f"p < 0.001")
    elif 0.001 <= p_value <= 0.01:
        print(f"p = {round(p_value, 3)}")
    else:
        print(f"p = {round(p_value, 2)}")
