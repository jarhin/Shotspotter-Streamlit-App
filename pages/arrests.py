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

# read data
# rename column for shell casing
# fillna values for casings, injuries and arrests.
@st.cache_data
def load_data_incidents():
    df = pd.read_csv(
        os.path.join(
            os.path.dirname("__file__"),
            "Data/2018-2024_cambridge_shotspotter_incidents - cambridge_shotspotter_incidents_extended_geocoded.csv",
        ),
        header=0,
    ).rename(
        columns={
            "shell_casings": "casings"
        }
    ).fillna(
        {
            "casings": 0,
            "injuries": 0,
            "arrests": 0
        }
    )
    
    return df

# pipeline for all combinations & years
@st.cache_data
def year_alert_combinations_data_incidents():

    # load all data to be used
    df = load_data_incidents()

    # change columns and clean data
    df_summary = (
        df.groupby(["year", "shotspotter_alert"])
        .agg(
            event_counts=pd.NamedAgg(aggfunc="count", column="additional_details"),
            casings=pd.NamedAgg(column="casings", aggfunc="sum"),
            injuries=pd.NamedAgg(column="injuries", aggfunc="sum"),
            arrests=pd.NamedAgg(column="arrests", aggfunc="sum"),
        )
        .reset_index(drop=False)
    )

    # unique
    # [python - Create all possible combinations of multiple columns in a Pandas DataFrame - Stack Overflow](https://stackoverflow.com/questions/49980763/create-all-possible-combinations-of-multiple-columns-in-a-pandas-dataframe#58903268)

    columns_required = ["year", "shotspotter_alert"]
    uniques = [df_summary[i].unique().tolist() for i in columns_required]
    combinations_df = pd.DataFrame(product(*uniques), columns=columns_required)

    # extract values
    full_combinations_df = pd.merge(
        combinations_df, df_summary, on=columns_required, how="right"
    ).assign(
        casings=lambda x: x.casings.fillna(0),
        injuries=lambda x: x.injuries.fillna(0),
        arrests=lambda x: x.arrests.fillna(0),
    )

    return full_combinations_df

# load data
df = load_data_incidents()

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

# functions to load ans store session keys
def keep(key):
    # Copy from temporary widget key to permanent key
    st.session_state[key] = st.session_state['_'+key]

def unkeep(key):
    # Copy from permanent key to temporary widget key
    st.session_state['_'+key] = st.session_state[key]

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

#@st.cache_data
def executive_sumamry_dict_function():

    # get data
    selected_df_year = st.session_state["selected_df_year"]

    # column names for looping
    list_column_names = ["event_counts", "casings", "injuries", "arrests"]

    # dictionary of variables
    temp_dict_results = {}

    # create the loop
    for my_col in list_column_names:
        # create dataframe for aggregation
        temp_agg = (
            selected_df_year.groupby("shotspotter_alert")
            .agg(
                min_var=pd.NamedAgg(column=my_col, aggfunc="min"),
                max_var=pd.NamedAgg(column=my_col, aggfunc="max"),
                mean_var=pd.NamedAgg(column=my_col, aggfunc="mean"),
                count_var=pd.NamedAgg(column=my_col, aggfunc="count"),
                sum_var=pd.NamedAgg(column=my_col, aggfunc="sum"),
            )
            .reset_index()
        )

        # extract summary variables
        temp_dict_results["min_var_true" + "_" + my_col] = int(
            temp_agg[temp_agg["shotspotter_alert"] == True]["min_var"].values[0]
        )
        temp_dict_results["min_var_false" + "_" + my_col] = int(
            temp_agg[temp_agg["shotspotter_alert"] == False]["min_var"].values[0]
        )
        temp_dict_results["max_var_true" + "_" + my_col] = int(
            temp_agg[temp_agg["shotspotter_alert"] == True]["max_var"].values[0]
        )
        temp_dict_results["max_var_false" + "_" + my_col] = int(
            temp_agg[temp_agg["shotspotter_alert"] == False]["max_var"].values[0]
        )
        temp_dict_results["mean_var_true" + "_" + my_col] = round(
            float(temp_agg[temp_agg["shotspotter_alert"] == True]["mean_var"].values[0]),
            st.session_state["default_rounding"],
        )
        temp_dict_results["mean_var_false" + "_" + my_col] = round(
            float(temp_agg[temp_agg["shotspotter_alert"] == False]["mean_var"].values[0]),
            st.session_state["default_rounding"],
        )
        temp_dict_results["count_var_true" + "_" + my_col] = int(
            temp_agg[temp_agg["shotspotter_alert"] == True]["count_var"].values[0]
        )
        temp_dict_results["count_var_false" + "_" + my_col] = int(
            temp_agg[temp_agg["shotspotter_alert"] == False]["count_var"].values[0]
        )
        temp_dict_results["sum_var_true" + "_" + my_col] = int(
            temp_agg[temp_agg["shotspotter_alert"] == True]["sum_var"].values[0]
        )
        temp_dict_results["sum_var_false" + "_" + my_col] = int(
            temp_agg[temp_agg["shotspotter_alert"] == False]["sum_var"].values[0]
        )

        # word summary for sums
        temp_dict_results["sum_increase_decrease" + "_" + my_col] = (
            "increase"
            if temp_dict_results["sum_var_true" + "_" + my_col]
            >= temp_dict_results["sum_var_false" + "_" + my_col]
            else "decrease"
        )
        temp_dict_results["sum_increase_decrease" + "_prefix_" + my_col] = (
            "an"
            if temp_dict_results["sum_increase_decrease" + "_" + my_col] == "increase"
            else "a"
        )
        temp_dict_results["sum_percentage_diff_" + my_col] = (
            0
            if temp_dict_results["sum_var_false" + "_" + my_col] == 0
            else abs(
                temp_dict_results["sum_var_false" + "_" + my_col]
                - temp_dict_results["sum_var_true" + "_" + my_col]
            )
            / temp_dict_results["sum_var_false" + "_" + my_col]
        )

        # summary for means
        temp_dict_results["mean_diff_" + my_col] = float(
            temp_dict_results["mean_var_true" + "_" + my_col]
            - temp_dict_results["mean_var_false" + "_" + my_col]
        )
        temp_dict_results["mean_percentage_diff_" + my_col] = float(
            0
            if temp_dict_results["mean_var_false" + "_" + my_col] == 0
            else (
                temp_dict_results["mean_var_true" + "_" + my_col]
                - temp_dict_results["mean_var_false" + "_" + my_col]
            )
            / temp_dict_results["mean_var_false" + "_" + my_col]
        )

        # summary for counts
        temp_dict_results["count_years_" + my_col] = int(
            max(
                temp_dict_results["count_var_true_" + my_col],
                temp_dict_results["count_var_false_" + my_col],
            )
        )

    # all counts
    temp_dict_results["count_years"] = max(
        [temp_dict_results["count_years_" + my_col] for my_col in list_column_names]
    )

    return temp_dict_results

# create variable of summary since values used in other dashboard pages
st.session_state["dict_variables_summary"] = executive_sumamry_dict_function()


# get variables
selected_df_year = st.session_state["selected_df_year"]
df_filtered = st.session_state["data"]

# helper functions for line chart
def display_linechart_viz(y_col: str, color_col: str):
    st.line_chart(selected_df_year, x="year", y=y_col, color=color_col)


# helper function for map
def display_map_layer(my_radius_col: str, radius_size: int, opacity_value: float):
    # chart layer
    return pdk.Layer(
        "ScatterplotLayer",
        data=df_filtered,
        get_position=["longitute", "latitude"],
        get_fill_color="colour_map",
        get_radius=f"{my_radius_col} * {radius_size}",
        opacity=opacity_value,
        stroked=True,
        filled=True,
        pickable=True,
    )

# split longitude and latitude
# https://stackoverflow.com/questions/29550414/how-can-i-split-a-column-of-tuples-in-a-pandas-dataframe
df_filtered[["latitude", "longitute"]] = df_filtered["LAT_LON_arcgis"].str.extract(
    pat=r"(-?\d+\.\d+),\s*(-?\d+\.\d+)"
)

# change type
df_filtered = df_filtered.assign(
    latitude=df_filtered["latitude"].astype("float"),
    longitute=df_filtered["longitute"].astype("float"),
)


# Fix colours for map
df_filtered = df_filtered.assign(
    colour=np.where(df_filtered["shotspotter_alert"], "#ff0000", "#00ff00"),
    colour_map=df_filtered["shotspotter_alert"].apply(
        lambda row: st.session_state["colour_lookup"].get(row)
    ),
)


# set constant for events
df_filtered = df_filtered.assign(events=1)

# Fix colour
selected_df_year = selected_df_year.assign(
    colour=np.where(selected_df_year["shotspotter_alert"], "#ff0000", "#00ff00")
)

# common map objects
initial_viewing_state = pdk.data_utils.compute_view(
    df_filtered[["longitute", "latitude"]], view_proportion=1
)

# read shapefile
gpd_df = gpd.read_file(
    os.path.join(os.path.dirname("__file__"), "shp/cambridge_locations.shp")
)

# make geopandas dataframe without z points
gpd_2d_df = gpd.GeoDataFrame(
    geometry=gpd.points_from_xy(
        gpd_df.geometry.x,
        gpd_df.geometry.y
    )
)

# make multipoints for shotspotter devices
gpd_polygon_df = gpd_2d_df.dissolve()

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
st.header("Arrests")
st.write(f"We consider the arrests with no alerts as the baseline.")

# columns
a1, a2, a3, a4, a5 = st.columns(5)
a1.metric("No. Yr", f"{st.session_state["dict_variables_summary"]['count_years_arrests']}")
a2.metric(
    "Alert: Avg. No. Arrests Per Yr.",
    f"{st.session_state["dict_variables_summary"]['mean_var_true_arrests']:.2f}",
)
a3.metric(
    "No alert: Avg. No. Arrests Per Yr.",
    f"{st.session_state["dict_variables_summary"]['mean_var_false_arrests']:.2f}",
)
a4.metric(
    "Diff. Avg. No. Arrests Per Yr.",
    f"{st.session_state["dict_variables_summary"]['mean_diff_arrests']:.2f}",
)
a5.metric(
    "Percent Diff. Avg. No. Arrests Per Yr.",
    f"{st.session_state["dict_variables_summary"]['mean_percentage_diff_arrests']:.2%}",
)

st.header("Arrests Visualisations")
st.write(
    ":red[Red]: Shotspotter alert; :green[Green]: No Shotspotter alert; and :blue[Blue]: Public Shotspotter devices."
)

st.subheader("Arrests By Year and Alert")
display_linechart_viz(y_col="arrests", color_col="colour")

st.subheader("Locations of Arrests and Public Devices")
st.pydeck_chart(
    pdk.Deck(
        map_style=f"{st.session_state["_mapstyle"]}",  # 'light', 'dark', 'road'
        initial_view_state=initial_viewing_state,
        layers=[
            display_map_layer(
                my_radius_col="arrests",
                radius_size=st.session_state["radius_default"],
                opacity_value=st.session_state["opacity_default"],
            ),
            device_layer,
        ],
        tooltip={"text": "{date} at {time}: {arrests} arrest(s) at {location}"},
    )
)
