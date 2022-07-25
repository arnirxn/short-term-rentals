import os
import itertools
import math
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import folium


DEFAULT_FIG_HEIGHT = 400
DEFAULT_FIG_WIDTH = 600
DEFAULT_SUPER_HOST_COLOR = "#C80000"
DEFAULT_REGULAR_HOST_COLOR = "#577590"
DEFAULT_COLOR_MAPPING = {
    True: DEFAULT_SUPER_HOST_COLOR,
    "Superhost": DEFAULT_SUPER_HOST_COLOR,
    False: DEFAULT_REGULAR_HOST_COLOR,
    "Host": DEFAULT_REGULAR_HOST_COLOR,
}


def get_colors():
    """Returns a list of RGB colors."""
    colors = list(px.colors.qualitative.Set2)
    colors.extend(px.colors.qualitative.Pastel2)
    colors.extend(px.colors.qualitative.Dark2)
    colors.extend(px.colors.qualitative.Set3)
    colors.extend(px.colors.qualitative.Pastel)
    return colors


def update_fig_layout(
    fig,
    title=None,
    height=None,
    width=None,
    xaxis_title=None,
    yaxis_title=None,
    showlegend=False,
    legend_title=None,
    legend_yanchor=None,
    legend_xanchor=None,
):
    """Updates the figure layout of a Plotly figure."""

    width = width if width else DEFAULT_FIG_WIDTH
    height = height if height else DEFAULT_FIG_HEIGHT
    legend_yanchor = legend_yanchor if legend_yanchor else 1.15
    legend_xanchor = legend_xanchor if legend_xanchor else 0.5

    fig.update_layout(
        title_text=title,
        plot_bgcolor="#FFFFFF",
        height=height if height else DEFAULT_FIG_HEIGHT,
        width=width if width else DEFAULT_FIG_WIDTH,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        showlegend=showlegend,
        legend=dict(
            title=legend_title,
            orientation="h",
            yanchor="top",
            y=legend_yanchor,
            xanchor="center",
            x=legend_xanchor,
        ),
    )


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


def visualize_accomodations_on_map(df, fig_name=None, save_output=True, viz_dir=None):
    """Returns a folium.Map to visualise the listings from hosts and superhosts."""
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

    if save_output:
        fig_name = fig_name if fig_name else "box"
        m.save(os.path.join(viz_dir, f"{fig_name}.html"))

    return m


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
    legend_yanchor=None,
    legend_xanchor=None,
    save_output=True,
    viz_dir=None,
):
    """Returns a Plotly bar chart for given configs."""
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
        fig,
        title,
        height,
        width,
        xaxis_title,
        yaxis_title,
        showlegend,
        legend_title,
        legend_yanchor=legend_yanchor,
        legend_xanchor=legend_xanchor,
    )

    if save_output:
        fig_name = fig_name if fig_name else "bar"
        fig.write_html(os.path.join(viz_dir, f"{fig_name}.html"))
        fig.write_image(
            os.path.join(viz_dir, f"{fig_name}.png"),
            format="png",
            width=width,
            height=height,
            scale=10,
        )

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
    legend_yanchor=None,
    legend_xanchor=None,
    xaxis_title=None,
    yaxis_title=None,
    fig_name=None,
    save_output=True,
    viz_dir=None,
):
    """Returns a Plotly box plot for given configs."""
    fig = px.box(
        df,
        x=x,
        y=y,
        color=color if color else x,
        color_discrete_map=DEFAULT_COLOR_MAPPING,
    )

    update_fig_layout(
        fig,
        title,
        height,
        width,
        xaxis_title,
        yaxis_title,
        showlegend,
        legend_title,
        legend_yanchor,
        legend_xanchor,
    )

    if save_output:
        fig_name = fig_name if fig_name else "box"
        fig.write_html(os.path.join(viz_dir, f"{fig_name}.html"))
        fig.write_image(
            os.path.join(viz_dir, f"{fig_name}.png"),
            format="png",
            width=DEFAULT_FIG_WIDTH,
            height=DEFAULT_FIG_HEIGHT,
            scale=10,
        )

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
    save_output=True,
    viz_dir=None,
):
    """Returns a Plotly pie chart for given configs."""
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

    if save_output:
        fig_name = fig_name if fig_name else "pie"
        fig.write_html(os.path.join(viz_dir, f"{fig_name}.html"))
        fig.write_image(
            os.path.join(viz_dir, f"{fig_name}.png"),
            format="png",
            width=DEFAULT_FIG_WIDTH,
            height=DEFAULT_FIG_HEIGHT,
            scale=10,
        )

    return fig
