from functions import *


df = pd.read_csv("./temp.csv")

BASE_URL = "http://data.insideairbnb.com/the-netherlands/north-holland/amsterdam/2022-03-08/data/"
VIZ_OUT_DIR = os.path.join(".", "visualizations")

# Get and clean data
df = pd.read_csv(os.path.join(BASE_URL, "listings.csv.gz"), compression="gzip")
clean_dataframe(df)

# Add columns
df["description_length"] = df["description"].fillna("").apply(lambda x: len(x))
df["host_about_length"] = df["host_about"].fillna("").apply(lambda x: len(x))
df["neighborhood_overview_length"] = df["neighborhood_overview"].fillna("").apply(lambda x: len(x))
df["number_of_amenities"] = df["amenities"].apply(lambda x: len(x))
df["number_of_host_verifications"] = df["host_verifications"].apply(lambda x: len(x)) # TODO: Fix list extraction
df["distance_to_centre_km"] = df.apply(lambda x: calculate_distance_to_amsterdam_centrum(x["latitude"], x["longitude"]), axis=1)
df["host_type"] = df["host_is_superhost"].replace([True, False], ["Superhost", "Host"])
df["review_scores_rating_bin"] = df["review_scores_rating"].round(0).astype("Int64")

# Splitting datasets
df_super = df.loc[df["host_is_superhost"]]
df_regular = df.loc[~df["host_is_superhost"]]

# Visualise on map
visualize_accomodations_on_map(df, fig_name="map")

# Pie chart percent superhost listings
# create_pie_chart(df, "host_type", title='Percentage of listings by host type', legend_title="Is Superhost")

### Bar charts
# Response time
metric = "host_response_time"
create_bar_chart(
    get_percent_count_groupby(df, ["host_type", metric]),
    x="percent",
    y=metric,
    color="host_type",
    orientation="h",
    fig_name=metric,
    width=600,
    height=400
)

# Host verified identity
metric = "host_identity_verified"
create_bar_chart(
    get_percent_count_groupby(df, ["host_type", metric]),
    x="percent",
    y=metric,
    color="host_type",
    # yaxis_title=metric,
    # legend_title="Host is superhost",
    orientation="h",
    fig_name=metric
)

# Location
metric = "neighbourhood_cleansed"
create_bar_chart(
    get_percent_count_groupby(df, ["host_type", metric]),
    x="percent",
    y=metric,
    color="host_type",
    orientation="h",
    width=600,
    height=600,
    legend_yanchor=1.1,
    fig_name=metric
)

### Box plots
# Availability 365
metric = "availability_365"
create_box_plot(
    remove_outliers(df.dropna(subset=[metric]), metric),
    x="host_type",
    y=metric,
    fig_name=metric
)
print_metric_mean_by_host_type(df, metric)

# Host acceptance rate
metric = "host_acceptance_rate"
create_box_plot(
    remove_outliers(df.dropna(subset=[metric]), metric),
    x="host_type",
    y=metric,
    fig_name=metric
)
print_metric_mean_by_host_type(df, metric)

# Reviews per month
metric = "reviews_per_month"
create_box_plot(
    remove_outliers(df.dropna(subset=[metric]), metric),
    x="host_type",
    y=metric,
    fig_name=metric
)
print_metric_mean_by_host_type(df, metric)

# Response rate
metric = "host_response_rate"
create_box_plot(
    remove_outliers(df.dropna(subset=[metric]), metric),
    x="host_type",
    y=metric,
    fig_name=metric
)
print_metric_mean_by_host_type(df, metric)

# Length of the description
metric = "description_length"
create_box_plot(
    remove_outliers(df.dropna(subset=[metric]), metric),
    x="host_type",
    y=metric,
    fig_name=metric
)
print_metric_mean_by_host_type(df, metric)

# Length of the host description
metric = "host_about_length"
create_box_plot(
    remove_outliers(df.dropna(subset=[metric]), metric),
    x="host_type",
    y=metric,
    fig_name=metric
)
print_metric_mean_by_host_type(df, metric)

# Length of the neighbourhood description
metric = "neighborhood_overview_length"
create_box_plot(
    remove_outliers(df.dropna(subset=[metric]), metric),
    x="host_type",
    y=metric,
    fig_name=metric
)
print_metric_mean_by_host_type(df, metric)

# Number of amenities
metric = "number_of_amenities"
create_box_plot(
    remove_outliers(df.dropna(subset=[metric]), metric),
    x="host_type",
    y=metric,
    fig_name=metric
)
print_metric_mean_by_host_type(df, metric)

# Number of host verifications
metric = "number_of_host_verifications"
create_box_plot(
    remove_outliers(df.dropna(subset=[metric]), metric),
    x="host_type",
    y=metric,
    fig_name=metric
)
print_metric_mean_by_host_type(df, metric)

# Number of host verifications
metric = "review_scores_rating"
create_box_plot(
    remove_outliers(df.dropna(subset=[metric]), metric),
    x="host_type",
    y=metric,
    fig_name=metric
)
print_metric_mean_by_host_type(df, metric)



### Print metrics
# Distance to centre
print(f"Average distance to centre Superhost listings: {df_super['distance_to_centre_km'].mean()} km")
print(f"Average distance to centre regular host listings: {df_regular['distance_to_centre_km'].mean()} km")
print(f"Average distance to centre Superhost listings: {df_super['distance_to_centre_km'].median()} km")
print(f"Average distance to centre regular host listings: {df_regular['distance_to_centre_km'].median()} km")

# Number of listings
print(f"Average number of listings to centre Superhost listings: {(df_super['host_total_listings_count'] > 1).sum() / df_super.shape[0]}")
print(f"Average number of listings to centre regular hosts listings: {(df_regular['host_total_listings_count'] > 1).sum() / df_regular.shape[0]}")

# Reviews
print_metric_mean_by_host_type(df, "review_scores_rating")
print_metric_mean_by_host_type(df, "review_scores_accuracy")
print_metric_mean_by_host_type(df, "review_scores_cleanliness")
print_metric_mean_by_host_type(df, "review_scores_checkin")
print_metric_mean_by_host_type(df, "review_scores_communication")
print_metric_mean_by_host_type(df, "review_scores_location")
print_metric_mean_by_host_type(df, "review_scores_value")

### T-tests: distance_to_centre_km,
