import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import datetime

st.set_page_config(
    page_title="CO2 Dashboard",
    page_icon="🌱",
    layout="wide"
)

# --------------------------------------------------
# Load Data
# --------------------------------------------------
@st.cache_data
def load_data():
    path = Path(__file__).parent / "co2_emissions.csv"
    df = pd.read_csv(path)

    df["Date"] = pd.to_datetime(
        df["Year"].astype(str) + "-01-01"
    )

    return df

df = load_data()

st.title("🌱 CO₂ Emissions Explorer")
st.caption("Interactive dashboard with filters and KPIs")

# --------------------------------------------------
# Sidebar Filters
# --------------------------------------------------
with st.sidebar:

    st.header("Filters")

    # Region Selectbox
    regions = ["All"] + sorted(df["Region"].unique())

    selected_region = st.selectbox(
        "Region",
        regions
    )

    # Chained Filter
    if selected_region == "All":
        country_options = sorted(df["Country"].unique())
    else:
        country_options = sorted(
            df[df["Region"] == selected_region]["Country"].unique()
        )

    # Country Multiselect
    selected_countries = st.multiselect(
        "Countries",
        country_options,
        default=country_options[:3]
    )

    # Date Input
    date_range = st.date_input(
        "Date Range",
        value=(
            datetime.date(2005, 1, 1),
            datetime.date(2020, 1, 1)
        ),
        min_value=datetime.date(
            int(df["Year"].min()), 1, 1
        ),
        max_value=datetime.date(
            int(df["Year"].max()), 1, 1
        )
    )

    # Metric Radio
    metric = st.radio(
        "Metric",
        [
            "Total CO2 (Mt)",
            "CO2 per capita"
        ]
    )

    # Checkbox
    highlight_top = st.checkbox(
        "Show only top emitter highlighted"
    )

# --------------------------------------------------
# Validation
# --------------------------------------------------
if not selected_countries:
    st.warning("Please select at least one country.")
    st.stop()

if len(date_range) != 2:
    st.warning("Please select both start and end date.")
    st.stop()

# --------------------------------------------------
# Convert Dates
# --------------------------------------------------
start_ts = pd.Timestamp(date_range[0])
end_ts = pd.Timestamp(date_range[1])

# --------------------------------------------------
# Filter Data
# --------------------------------------------------
filtered = df[
    (df["Country"].isin(selected_countries))
    &
    (df["Date"] >= start_ts)
    &
    (df["Date"] <= end_ts)
]

if filtered.empty:
    st.warning("No data matches your filters.")
    st.stop()

# --------------------------------------------------
# Metric Selection
# --------------------------------------------------
if metric == "Total CO2 (Mt)":
    y_col = "CO2_Mt"
    y_label = "CO2 Emissions (Mt)"
else:
    y_col = "CO2_per_capita"
    y_label = "CO2 per Capita"

# --------------------------------------------------
# KPI Row
# --------------------------------------------------
latest_year = filtered["Year"].max()

latest_data = filtered[
    filtered["Year"] == latest_year
]

total_latest = latest_data[y_col].sum()

first_year = filtered["Year"].min()

first_total = filtered[
    filtered["Year"] == first_year
][y_col].sum()

if first_total != 0:
    pct_change = (
        (total_latest - first_total)
        / first_total
    ) * 100
else:
    pct_change = 0

top_country = latest_data.loc[
    latest_data[y_col].idxmax(),
    "Country"
]

k1, k2, k3 = st.columns(3)

k1.metric(
    "Total CO2 (Latest Year)",
    f"{total_latest:,.0f}"
)

k2.metric(
    "% Change",
    f"{pct_change:.1f}%"
)

k3.metric(
    "Top Country",
    top_country
)

# --------------------------------------------------
# Filter Summary
# --------------------------------------------------
st.caption(
    f"{len(selected_countries)} countries | "
    f"{selected_region} | "
    f"{date_range[0]} to {date_range[1]} | "
    f"{metric} | "
    f"{len(filtered)} records"
)

# --------------------------------------------------
# Charts
# --------------------------------------------------
col_left, col_right = st.columns([2, 1])

# BBD colour type:
# Highlight colour + muted grey comparison lines

with col_left:

    if highlight_top:

        totals = (
            filtered.groupby("Country")[y_col]
            .sum()
            .sort_values(ascending=False)
        )

        top_emitter = totals.index[0]

        fig = px.line(
            filtered,
            x="Year",
            y=y_col,
            color="Country",
            title=f"{metric} Over Time"
        )

        for trace in fig.data:

            if trace.name == top_emitter:
                trace.line.width = 5
            else:
                trace.line.color = "lightgray"

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        fig = px.line(
            filtered,
            x="Year",
            y=y_col,
            color="Country",
            title=f"{metric} Over Time"
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# BBD colour type:
# Single colour ranking chart

with col_right:

    latest = filtered[
        filtered["Year"] == filtered["Year"].max()
    ].sort_values(y_col)

    fig2 = px.bar(
        latest,
        x=y_col,
        y="Country",
        orientation="h",
        title="Latest Year Ranking"
    )

    fig2.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )