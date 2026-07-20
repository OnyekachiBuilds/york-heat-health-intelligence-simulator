import json

import geopandas as gpd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from plotly.subplots import make_subplots


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="York Heat–Health Adaptation Animation",
    page_icon="🌡️",
    layout="wide",
)


# --------------------------------------------------
# LOAD YORK GIS DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    return geopandas_read()


def geopandas_read():
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
    "York Heat–Health Adaptation Scenario Animation"
)

st.write(
    "Compare how neighbourhood heat–health vulnerability changes "
    "as heatwave intensity increases, with and without a simulated "
    "30% urban greening intervention."
)

st.info(
    "Press ▶ Play below. Both maps advance through the same "
    "0°C to +5°C heatwave sequence using the same HHVI colour scale."
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
# MAP EXTENT
# --------------------------------------------------

bounds = map_gdf.total_bounds

centre_lon = (
    bounds[0] + bounds[2]
) / 2

centre_lat = (
    bounds[1] + bounds[3]
) / 2


# --------------------------------------------------
# FIXED GREENING INTERVENTION
# --------------------------------------------------

greening_percent = 30

greening_factor = (
    1 + greening_percent / 100
)

gdf["NDVI_Adaptation"] = (
    gdf["NDVI_mean"]
    * greening_factor
).clip(
    lower=0.0,
    upper=1.0,
)

gdf["NDVI_Adaptation_Change"] = (
    gdf["NDVI_Adaptation"]
    - gdf["NDVI_mean"]
).fillna(0.0)

gdf["Cooling_With_Greening"] = (
    gdf["Environmental_Cooling_Display"]
    - (
        1.81718582
        * gdf["NDVI_Adaptation_Change"]
    )
).clip(
    lower=0.0,
    upper=1.0,
)


# --------------------------------------------------
# SCENARIO CALCULATION FUNCTION
# --------------------------------------------------

def calculate_scenario(
    temperature_increase,
    use_greening=False,
):

    heat_hazard_change = (
        0.05065856129685917
        * temperature_increase
    )

    heat_hazard = (
        gdf["Heat_Hazard_Display"]
        + heat_hazard_change
    ).clip(
        lower=0.0,
        upper=1.0,
    )

    if use_greening:

        environmental_cooling = (
            gdf["Cooling_With_Greening"]
        )

    else:

        environmental_cooling = (
            gdf["Environmental_Cooling_Display"]
        )

    hhvi = (
        heat_hazard
        + environmental_cooling
        + gdf["Population_Sensitivity_Index"]
        + gdf["Social_Vulnerability_Display"]
    ) / 4

    hhvi_change = (
        hhvi
        - gdf["HHVI_Baseline"]
    )

    return (
        heat_hazard,
        environmental_cooling,
        hhvi,
        hhvi_change,
    )


# --------------------------------------------------
# TRACE CREATION FUNCTION
# --------------------------------------------------

def create_trace(
    temperature_increase,
    use_greening,
    subplot_name,
):

    (
        heat_hazard,
        environmental_cooling,
        hhvi,
        hhvi_change,
    ) = calculate_scenario(
        temperature_increase,
        use_greening,
    )

    customdata = np.column_stack(
        [
            gdf["LSOA21NM"].astype(str),
            gdf["HHVI_Baseline"].round(3),
            hhvi.round(3),
            hhvi_change.round(3),
            heat_hazard.round(3),
            environmental_cooling.round(3),
        ]
    )

    return go.Choroplethmap(
        geojson=geojson,

        locations=gdf["LSOA21CD"],

        featureidkey=(
            "properties.LSOA21CD"
        ),

        z=hhvi,

        customdata=customdata,

        coloraxis="coloraxis",

        marker=dict(
            opacity=0.82,
            line=dict(
                width=0.6,
            ),
        ),

        subplot=subplot_name,

        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Baseline HHVI: %{customdata[1]}<br>"
            "Scenario HHVI: %{customdata[2]}<br>"
            "Change: %{customdata[3]}<br>"
            "Heat Hazard: %{customdata[4]}<br>"
            "Environmental Cooling: %{customdata[5]}"
            "<extra></extra>"
        ),
    )


# --------------------------------------------------
# CREATE SIDE-BY-SIDE MAPS
# --------------------------------------------------

fig = make_subplots(
    rows=1,
    cols=2,

    specs=[
        [
            {
                "type": "map",
            },
            {
                "type": "map",
            },
        ]
    ],

    subplot_titles=(
        "Heatwave Only — No Adaptation",
        "Heatwave + 30% Urban Greening",
    ),

    horizontal_spacing=0.04,
)


# --------------------------------------------------
# INITIAL FRAME: 0°C
# --------------------------------------------------

fig.add_trace(
    create_trace(
        temperature_increase=0,
        use_greening=False,
        subplot_name="map",
    ),
    row=1,
    col=1,
)

fig.add_trace(
    create_trace(
        temperature_increase=0,
        use_greening=True,
        subplot_name="map2",
    ),
    row=1,
    col=2,
)


# --------------------------------------------------
# BUILD ANIMATION FRAMES
# --------------------------------------------------

frames = []

for temperature_increase in range(0, 6):

    heatwave_only_trace = create_trace(
        temperature_increase=temperature_increase,
        use_greening=False,
        subplot_name="map",
    )

    greening_trace = create_trace(
        temperature_increase=temperature_increase,
        use_greening=True,
        subplot_name="map2",
    )

    frame = go.Frame(

        name=str(
            temperature_increase
        ),

        data=[
            heatwave_only_trace,
            greening_trace,
        ],

        traces=[
            0,
            1,
        ],
    )

    frames.append(
        frame
    )


fig.frames = frames


# --------------------------------------------------
# SHARED COLOUR SCALE
# --------------------------------------------------

fig.update_layout(

    coloraxis=dict(

        colorscale=[
            [
                0.0,
                "#2ca25f",
            ],
            [
                0.33,
                "#fee08b",
            ],
            [
                0.66,
                "#f46d43",
            ],
            [
                1.0,
                "#a50026",
            ],
        ],

        cmin=0.30,

        cmax=0.85,

        colorbar=dict(
            title=(
                "Scenario<br>HHVI"
            ),

            thickness=18,
        ),
    ),
)


# --------------------------------------------------
# MAP CONFIGURATION
# --------------------------------------------------

fig.update_layout(

    map=dict(

        style=(
            "carto-positron"
        ),

        center=dict(
            lat=centre_lat,
            lon=centre_lon,
        ),

        zoom=9.4,
    ),

    map2=dict(

        style=(
            "carto-positron"
        ),

        center=dict(
            lat=centre_lat,
            lon=centre_lon,
        ),

        zoom=9.4,
    ),
)


# --------------------------------------------------
# PLAY / PAUSE BUTTONS
# --------------------------------------------------

fig.update_layout(

    updatemenus=[

        dict(

            type="buttons",

            direction="left",

            x=0.05,

            y=-0.08,

            showactive=False,

            buttons=[

                dict(

                    label="▶ Play",

                    method="animate",

                    args=[

                        None,

                        {

                            "frame": {

                                "duration": 1300,

                                "redraw": True,

                            },

                            "transition": {

                                "duration": 500,

                            },

                            "fromcurrent": True,

                            "mode": "immediate",

                        },

                    ],

                ),

                dict(

                    label="❚❚ Pause",

                    method="animate",

                    args=[

                        [None],

                        {

                            "frame": {

                                "duration": 0,

                                "redraw": False,

                            },

                            "transition": {

                                "duration": 0,

                            },

                            "mode": "immediate",

                        },

                    ],

                ),

            ],

        )

    ],
)


# --------------------------------------------------
# ANIMATION TIMELINE
# --------------------------------------------------

slider_steps = []

for temperature_increase in range(0, 6):

    slider_steps.append(

        dict(

            label=(
                f"+{temperature_increase}°C"
            ),

            method="animate",

            args=[

                [
                    str(
                        temperature_increase
                    )
                ],

                {

                    "frame": {

                        "duration": 0,

                        "redraw": True,

                    },

                    "transition": {

                        "duration": 300,

                    },

                    "mode": "immediate",

                },

            ],

        )

    )


fig.update_layout(

    sliders=[

        dict(

            active=0,

            currentvalue=dict(

                prefix=(
                    "Heatwave increase: "
                ),

                font=dict(
                    size=16,
                ),

            ),

            pad=dict(
                t=45,
            ),

            steps=slider_steps,

        )

    ],
)


# --------------------------------------------------
# OVERALL LAYOUT
# --------------------------------------------------

fig.update_layout(

    height=720,

    margin=dict(
        l=0,
        r=50,
        t=60,
        b=100,
    ),

    title=dict(

        text=(
            "York Heat–Health Vulnerability: "
            "Adaptation vs No Adaptation"
        ),

        x=0.5,

        xanchor="center",
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
# CITYWIDE COMPARISON TABLE
# --------------------------------------------------

comparison_rows = []

for temperature_increase in range(0, 6):

    (
        _,
        _,
        hhvi_no_adaptation,
        _,
    ) = calculate_scenario(
        temperature_increase,
        use_greening=False,
    )

    (
        _,
        _,
        hhvi_with_greening,
        _,
    ) = calculate_scenario(
        temperature_increase,
        use_greening=True,
    )

    comparison_rows.append(

        {

            "Heatwave Increase": (
                f"+{temperature_increase}°C"
            ),

            "Mean HHVI — No Adaptation": (
                hhvi_no_adaptation.mean()
            ),

            "Mean HHVI — 30% Greening": (
                hhvi_with_greening.mean()
            ),

            "Mean HHVI Reduction": (
                hhvi_no_adaptation.mean()
                - hhvi_with_greening.mean()
            ),

        }

    )


import pandas as pd

comparison_df = pd.DataFrame(
    comparison_rows
)

comparison_df[
    "Mean HHVI — No Adaptation"
] = comparison_df[
    "Mean HHVI — No Adaptation"
].round(3)

comparison_df[
    "Mean HHVI — 30% Greening"
] = comparison_df[
    "Mean HHVI — 30% Greening"
].round(3)

comparison_df[
    "Mean HHVI Reduction"
] = comparison_df[
    "Mean HHVI Reduction"
].round(3)


st.subheader(
    "Citywide Adaptation Comparison"
)

st.dataframe(
    comparison_df,
    hide_index=True,
    use_container_width=True,
)


# --------------------------------------------------
# INTERPRETATION
# --------------------------------------------------

st.info(
    "The left map represents increasing heat exposure without "
    "additional greening. The right map applies the same heatwave "
    "sequence while simulating a 30% proportional increase in NDVI. "
    "Because both maps use the same fixed HHVI colour scale, their "
    "differences can be compared directly."
)

st.warning(
    "The greening scenario is an exploratory planning scenario, "
    "not a prediction that a 30% increase in vegetation will produce "
    "an exact real-world reduction in heat-health impacts. The model "
    "shows how the validated York HHVI framework responds under the "
    "specified assumptions."
)