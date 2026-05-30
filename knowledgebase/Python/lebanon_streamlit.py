"""Streamlit app: estimated religious composition of Lebanon by district.

Run locally:   streamlit run lebanon_streamlit.py
Deploy:        push to GitHub and point Streamlit Community Cloud at this file.

DATA CAVEAT: Lebanon has held no official census since 1932. The percentages
below are rough estimates for illustration only, not authoritative statistics.
"""

import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

GEOJSON_URL = (
    "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/"
    "releaseData/gbOpen/LBN/ADM2/geoBoundaries-LBN-ADM2.geojson"
)

# Estimated Christian percentage per district (keys match geoBoundaries 'shapeName').
CHRISTIAN_PCT = {
    "Bcharre": 99, "Zgharta": 98, "Kesrouan": 97, "Jezzine": 95, "Batroun": 92,
    "Jbail": 88, "El Metn": 80, "Koura": 80, "Zahle": 65, "Aley": 50, "Baabda": 45,
    "Chouf": 45, "Beirut": 35, "Marjaayoun": 30, "Rachaya": 30, "Akkar": 25,
    "West Bekaa": 25, "Saida": 15, "Hasbaya": 15, "Baalbek": 10, "Sour": 5,
    "Tripoli": 5, "Hermel": 3, "Bent Jbail": 2, "Minieh-Dinnieh": 2, "Nabatiye": 1,
}
# Estimated Muslim (Sunni + Shia, excluding Druze) percentage per district.
MUSLIM_PCT = {
    "Bcharre": 1, "Zgharta": 2, "Kesrouan": 3, "Jezzine": 5, "Batroun": 8,
    "Jbail": 12, "El Metn": 20, "Koura": 20, "Zahle": 35, "Aley": 15, "Baabda": 53,
    "Chouf": 25, "Beirut": 63, "Marjaayoun": 65, "Rachaya": 40, "Akkar": 75,
    "West Bekaa": 70, "Saida": 85, "Hasbaya": 30, "Baalbek": 90, "Sour": 95,
    "Tripoli": 95, "Hermel": 97, "Bent Jbail": 98, "Minieh-Dinnieh": 98, "Nabatiye": 99,
}

LAYERS = {
    "Christian": ("christian_pct", "% Christian"),
    "Muslim": ("muslim_pct", "% Muslim"),
}


@st.cache_data(show_spinner="Loading district boundaries…")
def load_geojson() -> dict:
    return requests.get(GEOJSON_URL, timeout=120).json()


@st.cache_data
def build_dataframe(geojson: dict) -> pd.DataFrame:
    df = pd.DataFrame(
        [(f["properties"]["shapeName"],
          CHRISTIAN_PCT.get(f["properties"]["shapeName"]),
          MUSLIM_PCT.get(f["properties"]["shapeName"]))
         for f in geojson["features"]],
        columns=["district", "christian_pct", "muslim_pct"],
    )
    df["druze_other_pct"] = (100 - df["christian_pct"] - df["muslim_pct"]).clip(lower=0)
    return df.sort_values("christian_pct", ascending=False, ignore_index=True)


def make_map(df: pd.DataFrame, geojson: dict, column: str, label: str) -> go.Figure:
    fig = go.Figure(go.Choroplethmap(
        geojson=geojson,
        locations=df["district"],
        featureidkey="properties.shapeName",
        z=df[column],
        colorscale="RdYlBu",
        zmin=0, zmax=100,
        marker_opacity=0.78,
        marker_line_width=0.5,
        colorbar_title=label,
        customdata=df[["christian_pct", "muslim_pct", "druze_other_pct"]],
        hovertemplate=(
            "<b>%{location}</b><br>"
            "Christian: %{customdata[0]}%<br>"
            "Muslim: %{customdata[1]}%<br>"
            "Druze / other: %{customdata[2]}%<extra></extra>"
        ),
    ))
    fig.update_layout(
        map_style="carto-positron",
        map_center={"lat": 33.85, "lon": 35.86},
        map_zoom=7.2,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=620,
    )
    return fig


def make_bar(df: pd.DataFrame) -> go.Figure:
    order = df["district"].tolist()[::-1]
    colors = {"Christian": "#3b6fb6", "Muslim": "#2ca25f", "Druze / other": "#d9a441"}
    fig = go.Figure()
    for name, col in [("Christian", "christian_pct"),
                      ("Muslim", "muslim_pct"),
                      ("Druze / other", "druze_other_pct")]:
        fig.add_bar(y=order, x=df.set_index("district").loc[order, col],
                    name=name, orientation="h", marker_color=colors[name])
    fig.update_layout(
        barmode="group", height=820,
        margin={"l": 0, "r": 20, "t": 10, "b": 0},
        xaxis_title="% of population (est.)",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
    )
    return fig


def main() -> None:
    st.set_page_config(page_title="Lebanon — Religious Composition", layout="wide")

    st.title("Lebanon — Estimated Religious Composition by District")
    st.warning(
        "**Data caveat:** Lebanon has held no official census since 1932. "
        "These percentages are **rough estimates for illustration only**, not "
        "authoritative statistics. Christian % + Muslim % need not sum to 100 — "
        "the **Druze** (sizeable in Aley, Chouf, Hasbaya, Rachaya) are counted separately."
    )

    geojson = load_geojson()
    df = build_dataframe(geojson)

    layer_name = st.sidebar.radio("Map layer", list(LAYERS), index=0)
    st.sidebar.caption("Boundaries: geoBoundaries (ADM2). Toggle the religion shown on the map.")
    column, label = LAYERS[layer_name]

    tab_map, tab_bar, tab_data = st.tabs(["🗺️ Map", "📊 Breakdown", "🔢 Data"])
    with tab_map:
        st.subheader(f"Estimated {label.replace('% ', '')} population by district")
        st.plotly_chart(make_map(df, geojson, column, label), use_container_width=True)
    with tab_bar:
        st.subheader("Christian vs Muslim vs Druze/other share by district")
        st.plotly_chart(make_bar(df), use_container_width=True)
    with tab_data:
        st.dataframe(
            df.rename(columns={
                "district": "District", "christian_pct": "Christian %",
                "muslim_pct": "Muslim %", "druze_other_pct": "Druze / other %",
            }),
            use_container_width=True, hide_index=True,
        )


if __name__ == "__main__":
    main()
