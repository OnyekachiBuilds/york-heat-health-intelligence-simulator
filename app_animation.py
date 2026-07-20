import json

import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="York Heat–Health Animation",
    page_icon="🌡️",
    layout="wide",
)


# --------------------------------------------------
# LOAD YORK GIS DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    return gpd.read_file(
        "data/york_heat_health_clean.gpkg",
        layer="York_HeatHealth_Clean",
    )


gdf = load_data()


# --------------------------------------------------
# VALIDATED BASELINE ENGINE
# --------------------------------------------------

social_vulnerability_mean = (
    gdf["Social_Vulnerability_Index"].mean()
)

gdf["Social_Vulnerability_Display"] = (
    gdf["Social_Vulnerability_Index"]
    .fillna(social_vulnerability_mean)
)

gdf["HHVI_Baseline"] = (
    gdf["Heat_Hazard_Display"]
    + gdf["Environmental_Cooling_Display"]
    + gdf["Population_Sensitivity_Index"]
    + gdf["Social_Vulnerability_Display"]
) / 4


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title(
    "York Heat–Health Vulnerability Animation"
)

st.write(
    "Watch how neighbourhood heat–health vulnerability changes "
    "as a simulated heatwave intensifies from the baseline "
    "condition to +5°C."
)

st.info(
    "Press ▶ Play on the map to animate the heatwave scenario."
)


# --------------------------------------------------
# PREPARE MAP GEOMETRY
# --------------------------------------------------

map_gdf = (
    gdf[
        [
            "LSOA21CD",
            "LSOA21NM",
            "geometry",
        ]
    ]
    .to_crs(epsg=4326)
    .copy()
)

geojson = json.loads(
    map_gdf.to_json()
)


# --------------------------------------------------
# CREATE ANIMATION FRAMES
# --------------------------------------------------

animation_frames = []

for temperature_increase in range(0, 6):

    # --------------------------------------------------
    # HEAT HAZARD SCENARIO
    # --------------------------------------------------

    heat_hazard_change = (
        0.05065856129685917
        * temperature_increase
    )

    heat_hazard_scenario = (
        gdf["Heat_Hazard_Display"]
        + heat_hazard_change
    ).clip(
        lower=0.0,
        upper=1.0,
    )


    # --------------------------------------------------
    # HHVI SCENARIO
    # --------------------------------------------------

    hhvi_scenario = (
        heat_hazard_scenario
        + gdf["Environmental_Cooling_Display"]
        + gdf["Population_Sensitivity_Index"]
        + gdf["Social_Vulnerability_Display"]
    ) / 4


    # --------------------------------------------------
    # CHANGE FROM BASELINE
    # --------------------------------------------------

    hhvi_change = (
        hhvi_scenario
        - gdf["HHVI_Baseline"]
    )


    # --------------------------------------------------
    # BUILD FRAME
    # --------------------------------------------------

    frame = pd.DataFrame(
        {
            "LSOA21CD": gdf["LSOA21CD"],
            "Neighbourhood": gdf["LSOA21NM"],

            "Heatwave Increase": (
                f"+{temperature_increase}°C"
            ),

            "Frame_Order": (
                temperature_increase
            ),

            "Baseline HHVI": (
                gdf["HHVI_Baseline"]
                .round(3)
            ),

            "Scenario HHVI": (
                hhvi_scenario
                .round(3)
            ),

            "Change from Baseline": (
                hhvi_change
                .round(3)
            ),

            "Heat Hazard": (
                heat_hazard_scenario
                .round(3)
            ),
        }
    )

    animation_frames.append(
        frame
    )


animation_df = pd.concat(
    animation_frames,
    ignore_index=True,
)


# --------------------------------------------------
# MAP EXTENT
# --------------------------------------------------

bounds = (
    map_gdf.total_bounds
)

centre_lon = (
    bounds[0]
    + bounds[2]
) / 2

centre_lat = (
    bounds[1]
    + bounds[3]
) / 2


# --------------------------------------------------
# CREATE ANIMATED CHOROPLETH
# --------------------------------------------------

fig = px.choropleth_map(
    animation_df,

    geojson=geojson,

    locations="LSOA21CD",

    featureidkey=(
        "properties.LSOA21CD"
    ),

    color="Scenario HHVI",

    animation_frame=(
        "Frame_Order"
    ),

    hover_name=(
        "Neighbourhood"
    ),

    hover_data={
        "Heatwave Increase": True,
        "Baseline HHVI": ":.3f",
        "Scenario HHVI": ":.3f",
        "Change from Baseline": ":.3f",
        "Heat Hazard": ":.3f",
        "LSOA21CD": False,
        "Frame_Order": False,
    },

    color_continuous_scale=[
        "#2ca25f",
        "#fee08b",
        "#f46d43",
        "#a50026",
    ],

    range_color=(
        0.30,
        0.85,
    ),

    center={
        "lat": centre_lat,
        "lon": centre_lon,
    },

    zoom=9.7,

    map_style=(
        "carto-positron"
    ),

    opacity=0.80,

    labels={
        "Scenario HHVI":
            "Heat–Health Vulnerability",
        "Frame_Order":
            "Heatwave Increase (°C)",
    },
)


# --------------------------------------------------
# IMPROVE ANIMATION SPEED
# --------------------------------------------------

if fig.layout.updatemenus:

    fig.layout.updatemenus[0].buttons[0].args[1][
        "frame"
    ]["duration"] = 1200

    fig.layout.updatemenus[0].buttons[0].args[1][
        "transition"
    ]["duration"] = 600


# --------------------------------------------------
# MAP LAYOUT
# --------------------------------------------------

fig.update_layout(

    height=720,

    margin=dict(
        l=0,
        r=0,
        t=30,
        b=0,
    ),

    coloraxis_colorbar=dict(
        title="HHVI",
    ),
)


# --------------------------------------------------
# DISPLAY ANIMATION
# --------------------------------------------------

st.plotly_chart(
    fig,
    use_container_width=True,
)


# --------------------------------------------------
# EXPLANATION
# --------------------------------------------------

st.caption(
    "The animation holds population sensitivity, social "
    "vulnerability and environmental cooling constant while "
    "increasing the heat hazard component from +0°C to +5°C. "
    "The colour scale remains fixed across all frames so changes "
    "are directly comparable."
)

st.warning(
    "This is a scenario animation based on the validated "
    "HHVI_Display_1 framework. It illustrates modelled changes "
    "in vulnerability and is not a physical forecast of future "
    "temperature or health outcomes."
)