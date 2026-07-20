import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
import plotly.express as px

from branca.colormap import LinearColormap
from streamlit_folium import st_folium


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="York Heat–Health Intelligence Simulator",
    page_icon="🌡️",
    layout="wide",
)


# --------------------------------------------------
# LOAD DATA
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
    "York Heat–Health Intelligence Simulator"
)

st.write(
    "Explore how heatwave conditions and urban greening "
    "interventions may change neighbourhood heat–health "
    "vulnerability across York."
)


# --------------------------------------------------
# SCENARIO CONTROLS
# --------------------------------------------------

st.sidebar.header("Scenario Controls")

heatwave_increase = st.sidebar.slider(
    "Heatwave temperature increase (°C)",
    min_value=0.0,
    max_value=5.0,
    value=0.0,
    step=0.5,
)

greening_increase = st.sidebar.slider(
    "Urban greening intervention (%)",
    min_value=0,
    max_value=30,
    value=0,
    step=5,
)


# --------------------------------------------------
# HEATWAVE SCENARIO ENGINE
# --------------------------------------------------

heat_hazard_change = (
    0.05065856129685917
    * heatwave_increase
)

gdf["Heat_Hazard_Scenario"] = (
    gdf["Heat_Hazard_Display"]
    + heat_hazard_change
).clip(
    lower=0.0,
    upper=1.0,
)


# --------------------------------------------------
# GREENING SCENARIO ENGINE
# --------------------------------------------------

greening_factor = (
    1
    + greening_increase / 100
)

gdf["NDVI_Scenario"] = (
    gdf["NDVI_mean"]
    * greening_factor
).clip(
    lower=0.0,
    upper=1.0,
)

gdf["NDVI_Change"] = (
    gdf["NDVI_Scenario"]
    - gdf["NDVI_mean"]
).fillna(0.0)

gdf["Environmental_Cooling_Scenario"] = (
    gdf["Environmental_Cooling_Display"]
    - (
        1.81718582
        * gdf["NDVI_Change"]
    )
).clip(
    lower=0.0,
    upper=1.0,
)


# --------------------------------------------------
# FINAL SCENARIO HHVI
# --------------------------------------------------

gdf["HHVI_Scenario"] = (
    gdf["Heat_Hazard_Scenario"]
    + gdf["Environmental_Cooling_Scenario"]
    + gdf["Population_Sensitivity_Index"]
    + gdf["Social_Vulnerability_Display"]
) / 4


# --------------------------------------------------
# CHANGE FROM BASELINE
# --------------------------------------------------

gdf["HHVI_Change"] = (
    gdf["HHVI_Scenario"]
    - gdf["HHVI_Baseline"]
)


# --------------------------------------------------
# FIXED VULNERABILITY CLASSES
# --------------------------------------------------

hhvi_bins = [
    -float("inf"),
    0.4099303348553811,
    0.48065893067739107,
    0.553719429603365,
    float("inf"),
]

hhvi_labels = [
    "Low",
    "Moderate",
    "High",
    "Very High",
]

gdf["Baseline_Class"] = pd.cut(
    gdf["HHVI_Baseline"],
    bins=hhvi_bins,
    labels=hhvi_labels,
    include_lowest=True,
)

gdf["Scenario_Class"] = pd.cut(
    gdf["HHVI_Scenario"],
    bins=hhvi_bins,
    labels=hhvi_labels,
    include_lowest=True,
)


# --------------------------------------------------
# CLASS TRANSITIONS
# --------------------------------------------------

class_rank = {
    "Low": 1,
    "Moderate": 2,
    "High": 3,
    "Very High": 4,
}

gdf["Baseline_Class_Rank"] = (
    gdf["Baseline_Class"]
    .astype(str)
    .map(class_rank)
)

gdf["Scenario_Class_Rank"] = (
    gdf["Scenario_Class"]
    .astype(str)
    .map(class_rank)
)

gdf["Class_Transition"] = (
    gdf["Scenario_Class_Rank"]
    - gdf["Baseline_Class_Rank"]
)

class_improved = (
    gdf["Class_Transition"] < 0
).sum()

class_unchanged = (
    gdf["Class_Transition"] == 0
).sum()

class_worsened = (
    gdf["Class_Transition"] > 0
).sum()


# --------------------------------------------------
# SUMMARY CALCULATIONS
# --------------------------------------------------

baseline_mean = gdf["HHVI_Baseline"].mean()

scenario_mean = gdf["HHVI_Scenario"].mean()

hhvi_change = (
    scenario_mean
    - baseline_mean
)

if abs(hhvi_change) < 0.0005:
    hhvi_change = 0.0

improved_lsoas = (
    gdf["HHVI_Change"] < -0.01
).sum()

stable_lsoas = (
    gdf["HHVI_Change"].abs() <= 0.01
).sum()

worsened_lsoas = (
    gdf["HHVI_Change"] > 0.01
).sum()


# --------------------------------------------------
# SCENARIO INTELLIGENCE
# --------------------------------------------------

st.subheader("Scenario Intelligence")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Heatwave Increase",
        f"+{heatwave_increase:.1f} °C",
    )

with col2:
    st.metric(
        "Urban Greening",
        f"+{greening_increase}%",
    )

with col3:
    st.metric(
        "Baseline Mean HHVI",
        f"{baseline_mean:.3f}",
    )

with col4:
    st.metric(
        "Scenario Mean HHVI",
        f"{scenario_mean:.3f}",
        delta=f"{hhvi_change:+.3f}",
    )


# --------------------------------------------------
# SCENARIO CLASS COUNTS
# --------------------------------------------------

st.subheader(
    "Scenario Vulnerability Classes"
)

class_counts = (
    gdf["Scenario_Class"]
    .value_counts()
    .reindex(
        [
            "Low",
            "Moderate",
            "High",
            "Very High",
        ],
        fill_value=0,
    )
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Low",
        int(class_counts["Low"]),
    )

with c2:
    st.metric(
        "Moderate",
        int(class_counts["Moderate"]),
    )

with c3:
    st.metric(
        "High",
        int(class_counts["High"]),
    )

with c4:
    st.metric(
        "Very High",
        int(class_counts["Very High"]),
    )


# --------------------------------------------------
# CLASS TRANSITION SUMMARY
# --------------------------------------------------

st.subheader(
    "Vulnerability Class Transitions"
)

t1, t2, t3 = st.columns(3)

with t1:
    st.metric(
        "Moved to Lower Class",
        int(class_improved),
    )

with t2:
    st.metric(
        "Stayed in Same Class",
        int(class_unchanged),
    )

with t3:
    st.metric(
        "Moved to Higher Class",
        int(class_worsened),
    )


# --------------------------------------------------
# NUMERICAL NEIGHBOURHOOD RESPONSE
# --------------------------------------------------

st.subheader(
    "Neighbourhood Response"
)

r1, r2, r3 = st.columns(3)

with r1:
    st.metric(
        "LSOAs Improved",
        int(improved_lsoas),
    )

with r2:
    st.metric(
        "Little / No Change",
        int(stable_lsoas),
    )

with r3:
    st.metric(
        "LSOAs Worsened",
        int(worsened_lsoas),
    )


# --------------------------------------------------
# PRIORITY NEIGHBOURHOODS
# --------------------------------------------------

st.subheader(
    "Top Scenario-Priority Neighbourhoods"
)

priority_df = (
    gdf[
        [
            "LSOA21NM",
            "HHVI_Baseline",
            "HHVI_Scenario",
            "HHVI_Change",
            "Baseline_Class",
            "Scenario_Class",
            "Dominant_Driver",
            "Recommended_Action",
        ]
    ]
    .sort_values(
        "HHVI_Scenario",
        ascending=False,
    )
    .head(10)
    .copy()
)

priority_df.insert(
    0,
    "Rank",
    range(
        1,
        len(priority_df) + 1,
    ),
)

priority_df["HHVI_Baseline"] = (
    priority_df["HHVI_Baseline"]
    .round(3)
)

priority_df["HHVI_Scenario"] = (
    priority_df["HHVI_Scenario"]
    .round(3)
)

priority_df["HHVI_Change"] = (
    priority_df["HHVI_Change"]
    .round(3)
)

priority_df = priority_df.rename(
    columns={
        "LSOA21NM": "Neighbourhood",
        "HHVI_Baseline": "Baseline HHVI",
        "HHVI_Scenario": "Scenario HHVI",
        "HHVI_Change": "Change",
        "Baseline_Class": "Baseline Class",
        "Scenario_Class": "Scenario Class",
        "Dominant_Driver": "Dominant Driver",
        "Recommended_Action": "Recommended Action",
    }
)

st.dataframe(
    priority_df,
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "Neighbourhoods are ranked by Scenario HHVI. "
    "A neighbourhood may improve relative to baseline while "
    "remaining a high priority because its absolute vulnerability "
    "is still among the highest in York."
)


# --------------------------------------------------
# BASELINE VS SCENARIO SCATTER PLOT
# --------------------------------------------------

st.subheader(
    "Baseline vs Scenario HHVI"
)

chart_df = gdf[
    [
        "LSOA21NM",
        "HHVI_Baseline",
        "HHVI_Scenario",
        "HHVI_Change",
    ]
].copy()

fig = px.scatter(
    chart_df,
    x="HHVI_Baseline",
    y="HHVI_Scenario",
    hover_name="LSOA21NM",
    hover_data={
        "HHVI_Baseline": ":.3f",
        "HHVI_Scenario": ":.3f",
        "HHVI_Change": ":.3f",
    },
    labels={
        "HHVI_Baseline": "Baseline HHVI",
        "HHVI_Scenario": "Scenario HHVI",
    },
)

min_value = min(
    chart_df["HHVI_Baseline"].min(),
    chart_df["HHVI_Scenario"].min(),
)

max_value = max(
    chart_df["HHVI_Baseline"].max(),
    chart_df["HHVI_Scenario"].max(),
)

fig.add_shape(
    type="line",
    x0=min_value,
    y0=min_value,
    x1=max_value,
    y1=max_value,
    line=dict(
        dash="dash",
    ),
)

fig.update_layout(
    height=520,
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

st.caption(
    "Points above the dashed line have higher simulated "
    "vulnerability than baseline. Points below the line "
    "have lower simulated vulnerability."
)


# --------------------------------------------------
# MAP MODE
# --------------------------------------------------

st.subheader(
    "York Neighbourhood Intelligence Map"
)

map_mode = st.radio(
    "Choose map view",
    [
        "Scenario HHVI",
        "Change from Baseline",
    ],
    horizontal=True,
)


# --------------------------------------------------
# PREPARE MAP DATA
# --------------------------------------------------

map_gdf = (
    gdf
    .to_crs(epsg=4326)
    .copy()
)

map_gdf["Baseline_HHVI_Map"] = (
    map_gdf["HHVI_Baseline"]
    .round(3)
)

map_gdf["Scenario_HHVI_Map"] = (
    map_gdf["HHVI_Scenario"]
    .round(3)
)

map_gdf["HHVI_Change_Map"] = (
    map_gdf["HHVI_Change"]
    .round(3)
)

map_gdf["Heat_Hazard_Map"] = (
    map_gdf["Heat_Hazard_Scenario"]
    .round(3)
)

map_gdf["Cooling_Map"] = (
    map_gdf[
        "Environmental_Cooling_Scenario"
    ]
    .round(3)
)


# --------------------------------------------------
# MAP EXTENT
# --------------------------------------------------

bounds = map_gdf.total_bounds

min_lon = bounds[0]
min_lat = bounds[1]
max_lon = bounds[2]
max_lat = bounds[3]

centre_lat = (
    min_lat + max_lat
) / 2

centre_lon = (
    min_lon + max_lon
) / 2


# --------------------------------------------------
# BASE MAP
# --------------------------------------------------

m = folium.Map(
    location=[
        centre_lat,
        centre_lon,
    ],
    zoom_start=11,
    tiles="CartoDB positron",
)


# --------------------------------------------------
# SCENARIO HHVI VIEW
# --------------------------------------------------

if map_mode == "Scenario HHVI":

    colour_scale = LinearColormap(
        colors=[
            "#2ca25f",
            "#fee08b",
            "#f46d43",
            "#a50026",
        ],
        vmin=0.30,
        vmax=0.85,
    )

    colour_scale.caption = (
        "Scenario Heat–Health Vulnerability Index"
    )

    folium.GeoJson(
        data=map_gdf,

        style_function=lambda feature: {
            "fillColor": colour_scale(
                feature["properties"][
                    "HHVI_Scenario"
                ]
            ),
            "color": "#555555",
            "weight": 0.7,
            "fillOpacity": 0.80,
        },

        highlight_function=lambda feature: {
            "weight": 3,
            "color": "#000000",
            "fillOpacity": 0.95,
        },

        tooltip=folium.GeoJsonTooltip(
            fields=[
                "LSOA21NM",
                "Baseline_HHVI_Map",
                "Scenario_HHVI_Map",
                "HHVI_Change_Map",
                "Heat_Hazard_Map",
                "Cooling_Map",
            ],

            aliases=[
                "Neighbourhood:",
                "Baseline HHVI:",
                "Scenario HHVI:",
                "Change from Baseline:",
                "Scenario Heat Hazard:",
                "Environmental Cooling:",
            ],

            sticky=False,
        ),

    ).add_to(m)

    colour_scale.add_to(m)


# --------------------------------------------------
# CHANGE MAP VIEW
# --------------------------------------------------

else:

    def change_colour(value):

        if value is None:
            return "#bdbdbd"

        if value <= -0.03:
            return "#006837"

        elif value <= -0.01:
            return "#78c679"

        elif value < 0.01:
            return "#d9d9d9"

        elif value < 0.03:
            return "#fdae61"

        else:
            return "#d73027"


    folium.GeoJson(
        data=map_gdf,

        style_function=lambda feature: {
            "fillColor": change_colour(
                feature["properties"][
                    "HHVI_Change"
                ]
            ),
            "color": "#555555",
            "weight": 0.7,
            "fillOpacity": 0.85,
        },

        highlight_function=lambda feature: {
            "weight": 3,
            "color": "#000000",
            "fillOpacity": 1.0,
        },

        tooltip=folium.GeoJsonTooltip(
            fields=[
                "LSOA21NM",
                "Baseline_HHVI_Map",
                "Scenario_HHVI_Map",
                "HHVI_Change_Map",
                "Heat_Hazard_Map",
                "Cooling_Map",
            ],

            aliases=[
                "Neighbourhood:",
                "Baseline HHVI:",
                "Scenario HHVI:",
                "Change from Baseline:",
                "Scenario Heat Hazard:",
                "Environmental Cooling:",
            ],

            sticky=False,
        ),

    ).add_to(m)


    legend_html = """
    <div style="
        position: fixed;
        bottom: 40px;
        left: 40px;
        z-index: 9999;
        background-color: white;
        border: 1px solid #777;
        border-radius: 6px;
        padding: 12px;
        font-size: 13px;
        line-height: 1.6;
    ">

    <b>Change in HHVI</b><br>

    <span style="display:inline-block;width:14px;height:14px;background:#006837;"></span>
    Strong improvement ≤ -0.03<br>

    <span style="display:inline-block;width:14px;height:14px;background:#78c679;"></span>
    Moderate improvement<br>

    <span style="display:inline-block;width:14px;height:14px;background:#d9d9d9;"></span>
    Little / no change<br>

    <span style="display:inline-block;width:14px;height:14px;background:#fdae61;"></span>
    Moderate worsening<br>

    <span style="display:inline-block;width:14px;height:14px;background:#d73027;"></span>
    Strong worsening ≥ +0.03

    </div>
    """

    m.get_root().html.add_child(
        folium.Element(
            legend_html
        )
    )


# --------------------------------------------------
# FIT MAP
# --------------------------------------------------

m.fit_bounds(
    [
        [
            min_lat,
            min_lon,
        ],
        [
            max_lat,
            max_lon,
        ],
    ]
)


# --------------------------------------------------
# DISPLAY MAP
# --------------------------------------------------

st_folium(
    m,
    width=None,
    height=650,
    use_container_width=True,
)


# --------------------------------------------------
# INTERPRETATION
# --------------------------------------------------

if map_mode == "Change from Baseline":

    st.info(
        "Green neighbourhoods show reductions in simulated "
        "heat–health vulnerability. Orange and red show "
        "increasing vulnerability. Grey indicates little "
        "or no meaningful numerical change."
    )

else:

    st.info(
        "This map shows absolute simulated heat–health "
        "vulnerability under the selected scenario."
    )


st.caption(
    "The simulator is derived from the validated "
    "HHVI_Display_1 baseline. Scenario outputs are exploratory "
    "decision-support results rather than deterministic predictions."
)