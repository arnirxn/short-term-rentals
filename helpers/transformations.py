import ast
from helpers.analyses import calculate_distance_to_amsterdam_centrum
import pandas as pd
import warnings


def drop_na_columns(df, percentage_threshold):
    """Removes columns from a pandas.DataFrame with missing values equla or higher to threshold."""
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


def remove_outliers(df, metric, sd_threshold=2, warning_treshold=0.05):
    """Removes outliers from a pandas.DataFrame for given standard deviation threshold."""
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


def add_columns_to_df(df):
    """Adds columns to a pandas.DataFrame relevant to the host analysis."""
    df["description_length"] = df["description"].fillna("").apply(lambda x: len(x))
    df["host_about_length"] = df["host_about"].fillna("").apply(lambda x: len(x))
    df["neighborhood_overview_length"] = (
        df["neighborhood_overview"].fillna("").apply(lambda x: len(x))
    )
    df["number_of_amenities"] = df["amenities"].apply(lambda x: len(x))
    df["number_of_host_verifications"] = df["host_verifications"].apply(
        lambda x: len(x)
    )
    df["distance_to_centre_km"] = df.apply(
        lambda x: calculate_distance_to_amsterdam_centrum(
            x["latitude"], x["longitude"]
        ),
        axis=1,
    )
    df["host_type"] = df["host_is_superhost"].replace(
        [True, False], ["Superhost", "Host"]
    )
    df["review_scores_rating_bin"] = df["review_scores_rating"].round(0).astype("Int64")
