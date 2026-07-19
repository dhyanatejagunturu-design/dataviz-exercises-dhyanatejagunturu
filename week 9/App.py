import os
import streamlit as st
import pandas as pd
import plotly.express as px

# ─────────────────────────────────────────────
# STEP 1 — LOAD DATA
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "week09", "world_happiness_2023.csv")

df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()

df = df.rename(columns={
    "Country name": "Country",
    "Regional indicator": "Region",
    "Ladder score": "Score",
    "Logged GDP per capita": "GDP",
    "Social support": "Social_Support",
    "Healthy life expectancy": "Life_Expectancy",
    "Freedom to make life choices": "Freedom",
    "Generosity": "Generosity",
    "Perceptions of corruption": "Corruption"
})

# ─────────────────────────────────────────────
# STEP 2 — PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="World Happiness Dashboard", layout="wide")

st.title("🌍 World Happiness Dashboard")
st.caption("World Happiness Report 2023")

# ─────────────────────────────────────────────
# STEP 3 — SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    regions = ["All"] + sorted(df["Region"].dropna().unique().tolist())
    selected_region = st.selectbox("Select Region", regions)

    top_n = st.slider("Top N Countries", 5, 25, 15)

filtered = df if selected_region == "All" else df[df["Region"] == selected_region]

# ─────────────────────────────────────────────
# STEP 4 — KPI METRICS
# ─────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

col1.metric("Countries", len(filtered))

col2.metric(
    "Average Score",
    f"{filtered['Score'].mean():.2f}"
)

col3.metric(
    "Happiest Country",
    filtered.loc[filtered["Score"].idxmax(), "Country"]
)

st.divider()

# ─────────────────────────────────────────────
# STEP 5 — MAIN CHARTS
# ─────────────────────────────────────────────
col_left, col_right = st.columns(2)

# --- TOP COUNTRIES BAR CHART ---
with col_left:
    st.subheader("Top Countries")

    top = filtered.nlargest(top_n, "Score").sort_values("Score")

    fig1 = px.bar(
        top,
        x="Score",
        y="Country",
        orientation="h",
        color="Score",
        color_continuous_scale="Blues"
    )

    fig1.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(fig1, use_container_width=True)

# --- GDP VS HAPPINESS SCATTER ---
with col_right:
    st.subheader("GDP vs Happiness")

    fig2 = px.scatter(
        filtered,
        x="GDP",
        y="Score",
        hover_name="Country",
        color="Region"
    )

    fig2.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# STEP 6 — DIVERGING CHART (FIXED + CLEAN)
# ─────────────────────────────────────────────
st.subheader("Freedom to Make Life Choices (Diverging View)")

mid = df["Freedom"].mean()

div_data = filtered.sort_values("Freedom")

fig3 = px.bar(
    div_data,
    x="Freedom",
    y="Country",
    orientation="h",
    color="Freedom",
    color_continuous_scale="RdBu",
    color_continuous_midpoint=mid
)

fig3.add_vline(x=mid, line_width=2, line_dash="dash")

fig3.add_annotation(
    x=mid,
    y=len(div_data) - 1,
    text="Global Average",
    showarrow=False,
    yshift=10
)

fig3.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.plotly_chart(fig3, use_container_width=True)