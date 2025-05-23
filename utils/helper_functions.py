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

def load_data_incidents_monthly():

    # find last csv file of month
    monthly_csv_directory = "./CSV/Monthly Reports/"

    # list of files with paths
    list_of_monthly_files = [
        os.path.join(
            monthly_csv_directory, 
            file
        ) for file in os.listdir(monthly_csv_directory)
    ]


    # last file by creation date
    path_to_last_csv_file = max(list_of_monthly_files, key=os.path.getctime)

    df = pd.read_csv(
        path_to_last_csv_file,
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

    # get extra data 
    aux_data = df[["page", "date_string", "path"]].drop_duplicates()

    # return dataframes
    return df.drop(columns=["page", "date_string", "path"]), aux_data


def load_data_incidents_yearly():

    # find all yearly files
    yearly_csv_directory = "./CSV/Yearly Reports/"

    # list of files with paths
    list_of_yearly_files = [
        os.path.join(
            yearly_csv_directory, 
            file
        ) for file in os.listdir(yearly_csv_directory)
    ]


    df = pd.concat(
                pd.read_csv(
                    file,
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
                ) for file in list_of_yearly_files
        )

    # get extra data 
    aux_data = df[["page", "date_string", "path"]].drop_duplicates()

    # return dataframes
    return df.drop(columns=["page", "date_string", "path"]), aux_data


def load_all_data():

    df1  = load_data_incidents()
    df2, aux_data2 = load_data_incidents_monthly()
    # df3, aux_data3 = load_data_incidents_yearly()

    # return pd.concat([df1, df2, df3], axis=0).drop(columns=["page", "date_string", "path"]), pd.concat([aux_data2, aux_data3], axis=0)
    return pd.concat([df1, df2], axis=0), pd.concat([aux_data2], axis=0)


# pipeline for all combinations & years
@st.cache_data
def year_alert_combinations_data_incidents():

    # load all data to be used
    # df = load_data_incidents()
    df, _ = load_all_data()

    # change columns and clean data
    df_summary = (
        df.groupby(["year", "shotspotter_alert"])
        .agg(
            event_counts=pd.NamedAgg(aggfunc="count", column="location"),
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

# functions to load ans store session keys
def keep(key):
    # Copy from temporary widget key to permanent key
    st.session_state[key] = st.session_state['_'+key]

def unkeep(key):
    # Copy from permanent key to temporary widget key
    st.session_state['_'+key] = st.session_state[key]

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




#@st.cache_data
def maps_pipeline_data():

    # load session data
    df_filtered = st.session_state["data"] 


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

    return df_filtered

#@st.cache_data
def chart_pipeline_data():

    # load data
    selected_df_year = st.session_state["selected_df_year"]

    # Fix colour
    selected_df_year = selected_df_year.assign(
        colour=np.where(selected_df_year["shotspotter_alert"], "#ff0000", "#00ff00")
    )

    return selected_df_year

@st.cache_data
def load_data_shapefile():

    # read shapefile
    gpd_df = gpd.read_file(
        os.path.join(
            os.path.dirname("__file__"), 
            "shp/cambridge_locations.shp"
        )
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

    return gpd_polygon_df

# helper functions for line chart
def display_linechart_viz(y_col: str, color_col: str):
    st.line_chart(chart_pipeline_data(), x="year", y=y_col, color=color_col)


# helper function for map
def display_map_layer(my_radius_col: str, radius_size: int, opacity_value: float):
    # chart layer
    return pdk.Layer(
        "ScatterplotLayer",
        data=maps_pipeline_data(),
        get_position=["longitute", "latitude"],
        get_fill_color="colour_map",
        get_radius=f"{my_radius_col} * {radius_size}",
        opacity=opacity_value,
        stroked=True,
        filled=True,
        pickable=True,
    )