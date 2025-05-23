# libraries
import pandas as pd
import os
import streamlit as st
from itertools import product

# sklearn
from matplotlib import pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
import numpy as np

# typing
from typing import List
from typing import Optional

# more libs
import pydeck as pdk
import geopandas as gpd

# helper imports
from utils.helper_functions import * 

# load data
# df = load_data_incidents()
df, _ = load_all_data()

# extract min and max for global sliders
year_range_min = df["year"].min()
year_range_max = df["year"].max()

# load combinations + years
full_combinations_df = year_alert_combinations_data_incidents()

# session state
if "data" not in st.session_state:
    st.session_state["data"] = df
if "select_year_slider" not in st.session_state:
    st.session_state["select_year_slider"] = (year_range_min, year_range_max)
if "selected_df_year" not in st.session_state:
    st.session_state["selected_df_year"] = full_combinations_df
if "mapstyle" not in st.session_state:
    st.session_state["mapstyle"] = "light"
if "shotspotter_select" not in st.session_state:
    st.session_state["shotspotter_select"] = "Points"
if "default_rounding" not in st.session_state:
    st.session_state["default_rounding"] = 3
if "radius_default" not in st.session_state:
    st.session_state["radius_default"] = radius_default = 50
if "opacity_default" not in st.session_state:
    st.session_state["opacity_default"] = 0.5
if "colour_lookup" not in st.session_state:
    st.session_state["colour_lookup"] = {True: [255, 0, 0, 128], False: [0, 255, 0, 128]}

# global slider
unkeep("select_year_slider")
st.sidebar.slider(
    "Select a range of values", 
    min_value=year_range_min, 
    max_value=year_range_max, 
    # value = (year_range_min, year_range_max),
    key="_select_year_slider",
    on_change=keep,
    args=['select_year_slider']
)

# https://discuss.streamlit.io/t/changing-mapstyles-with-select-box/27069/2

# global slider 
# maps pages
unkeep("mapstyle")
st.sidebar.selectbox(
    "Choose Map Style:",
    options=["light", "dark", "road"],
    format_func=str.capitalize,
    key="_mapstyle",
    on_change=keep,
    args=['mapstyle']
)


# global slider 
# maps pages
unkeep("shotspotter_select")
st.sidebar.selectbox(
    "Choose Shotspotter Device Visualisation Type",
    options= [
        "Points", 
        "Concave Region", 
        "Convex Region", 
        "Circular Region", 
        "Rectangular Region"
    ],
    key="_shotspotter_select",
    on_change=keep,
    args=['shotspotter_select']

)

# update session data by filtering years
st.session_state["data"] = df[
    (df["year"] <= st.session_state["_select_year_slider"][1]) & (df["year"] >= st.session_state["_select_year_slider"][0])
]

# update selected_df_year by filtering years
st.session_state["selected_df_year"] = full_combinations_df[
    (
        (full_combinations_df["year"] <= st.session_state["_select_year_slider"][1])
        & (full_combinations_df["year"] >= st.session_state["_select_year_slider"][0])
    )
]

# create variable of summary since values used in other dashboard pages
st.session_state["dict_variables_summary"] = executive_sumamry_dict_function()

# get variables
selected_df_year = st.session_state["selected_df_year"]
df_filtered = maps_pipeline_data()

# common map objects
initial_viewing_state = pdk.data_utils.compute_view(
    df_filtered[["longitute", "latitude"]], view_proportion=1
)

# load data for shotspotter devices
gpd_polygon_df = load_data_shapefile()

# shotspotter device choices as dictionary
dictionary_pdk_layers = {
    "Points": pdk.Layer(
        "GeoJsonLayer",
        gpd_polygon_df,
        get_fill_color=[0, 0, 255],
        get_point_radius=10,
        opacity=0.25
    ),
    "Concave Region": pdk.Layer(
        "GeoJsonLayer",
        gpd_polygon_df.concave_hull(),
        get_fill_color=[0, 0, 255],
        get_point_radius=10,
        opacity=0.25
    ),
    "Convex Region": pdk.Layer(
        "GeoJsonLayer",
        gpd_polygon_df.convex_hull,
        get_fill_color=[0, 0, 255],
        get_point_radius=10,
        opacity=0.25
    ),
    "Circular Region": pdk.Layer(
        "GeoJsonLayer",
        gpd_polygon_df.minimum_bounding_circle(),
        get_fill_color=[0, 0, 255],
        get_point_radius=10,
        opacity=0.25
    ),
    "Rectangular Region": pdk.Layer(
        "GeoJsonLayer",
        gpd_polygon_df.envelope,
        get_fill_color=[0, 0, 255],
        get_point_radius=10,
        opacity=0.25
    )
}

# dictionary selection with default (i.e. points)
device_layer = dictionary_pdk_layers.get(
    st.session_state["_shotspotter_select"], 
    dictionary_pdk_layers["Points"]
)

# header
st.header("Bullet Casings")
st.write(f"We consider the events with no alerts as the baseline.")

# columns
a1, a2, a3 = st.columns(3)
b1, b2 = st.columns(2)

a1.metric("No. of Yr", f"{st.session_state["dict_variables_summary"]['count_years_casings']}")
a2.metric(
    "Alert: Avg. No. Bullet Casings Per Yr.",
    f"{st.session_state["dict_variables_summary"]['mean_var_true_casings']:.2f}",
)
a3.metric(
    "No alert: Avg. Bullet Casings Per Yr.",
    f"{st.session_state["dict_variables_summary"]['mean_var_false_casings']:.2f}",
)
b1.metric(
    "Diff. in Avg. Bullet Casings Per Yr.",
    f"{st.session_state["dict_variables_summary"]['mean_diff_casings']:.2f}",
)
b2.metric(
    "Percent Diff. in Avg. Bullet Casings Per Yr.",
    f"{st.session_state["dict_variables_summary"]['mean_percentage_diff_casings']:.2%}",
)

st.header("Casing Visualisations")
st.write(
    ":red[Red]: Shotspotter alert; :green[Green]: No Shotspotter alert; and :blue[Blue]: Public Shotspotter devices."
)

st.subheader("Bullet Casings By Year and Alert")
display_linechart_viz(y_col="event_counts", color_col="colour")

st.subheader("Locations of Bullet Casings and Public Devices")
st.pydeck_chart(
    pdk.Deck(
        map_style=f"{st.session_state["_mapstyle"]}",  # 'light', 'dark', 'road'
        initial_view_state=initial_viewing_state,
        layers=[
            display_map_layer(
                my_radius_col="casings",
                radius_size=st.session_state["radius_default"],
                opacity_value=st.session_state["opacity_default"],
            ),
            device_layer,
        ],
        tooltip={
            "text": "{date} at {time}: {casings} shell casing(s) at {location}"
        },
    )
)