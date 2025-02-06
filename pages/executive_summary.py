# libraries
import pandas as pd
import os
import streamlit as st
from itertools import product



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

# rounding
default_rounding = 3

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
            default_rounding,
        )
        temp_dict_results["mean_var_false" + "_" + my_col] = round(
            float(temp_agg[temp_agg["shotspotter_alert"] == False]["mean_var"].values[0]),
            default_rounding,
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


st.header("Executive Summary")
st.subheader("Number of Years")
st.write(
    f"We consider {st.session_state["dict_variables_summary"]['count_years']} years of selected data."
)
st.subheader("Events")
st.write(
    f"We find that a total of {st.session_state["dict_variables_summary"]['sum_var_false_event_counts']} non-Shotspotter events compared to a total of {st.session_state["dict_variables_summary"]['sum_var_true_event_counts']} Shotspotter events, which is {st.session_state["dict_variables_summary"]['sum_increase_decrease_event_counts']} {st.session_state["dict_variables_summary"]['sum_increase_decrease_prefix_event_counts']} of {st.session_state["dict_variables_summary"]['sum_percentage_diff_event_counts']:.2%} when we consider the non-Shotspotter events as the baseline."
)
st.subheader("Shell Casings")
st.write(
    f"We find that a total of {st.session_state["dict_variables_summary"]['sum_var_false_casings']} shell casings during non-Shotspotter events compared to a total of {st.session_state["dict_variables_summary"]['sum_var_true_casings']} shell casings during Shotspotter events, which is {st.session_state["dict_variables_summary"]['sum_increase_decrease_casings']} {st.session_state["dict_variables_summary"]['sum_increase_decrease_prefix_casings']} of {st.session_state["dict_variables_summary"]['sum_percentage_diff_casings']:.2%} when we consider the non-Shotspotter shell casings as the baseline."
)
st.subheader("Injuries")
st.write(
    f"We find that a total of {st.session_state["dict_variables_summary"]['sum_var_false_injuries']} injuries during non-Shotspotter events compared to a total of {st.session_state["dict_variables_summary"]['sum_var_true_injuries']} injuries during Shotspotter events, which is {st.session_state["dict_variables_summary"]['sum_increase_decrease_injuries']} {st.session_state["dict_variables_summary"]['sum_increase_decrease_prefix_injuries']} of {st.session_state["dict_variables_summary"]['sum_percentage_diff_injuries']:.2%} when we consider the non-Shotspotter injuries as the baseline."
)
st.subheader("Arrests")
st.write(
    f"We find that a total of {st.session_state["dict_variables_summary"]['sum_var_false_arrests']} arrests during non-Shotspotter events compared to a total of {st.session_state["dict_variables_summary"]['sum_var_true_arrests']} arrests during Shotspotter events, which is {st.session_state["dict_variables_summary"]['sum_increase_decrease_arrests']} {st.session_state["dict_variables_summary"]['sum_increase_decrease_prefix_arrests']} of {st.session_state["dict_variables_summary"]['sum_percentage_diff_arrests']:.2%} when we consider the non-Shotspotter arrests as the baseline."
)
