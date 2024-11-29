import pandas as pd
import os
import streamlit as st
from streamlit_dynamic_filters import DynamicFilters
from itertools import product
import numpy as np

# read file
df = pd.read_csv(
    os.path.join(
        os.path.dirname('__file__'), 
        "Data/2018-2024_cambridge_shotspotter_incidents - cambridge_shotspotter_incidents_extended_geocoded.csv"
        ),
        header=0 
)

df_summary = df.assign(
    shell_casings = lambda x: x.shell_casings.fillna(0),
    injuries = lambda x: x.injuries.fillna(0),
    arrests = lambda x: x.arrests.fillna(0)
).groupby(
    ["year", "shotspotter_alert"]
).agg(
    event_counts = pd.NamedAgg(aggfunc="count", column="additional_details"),
    shell_casings = pd.NamedAgg(column="shell_casings", aggfunc="sum"),
    injuries = pd.NamedAgg(column="injuries", aggfunc="sum"),
    arrests = pd.NamedAgg(column="arrests", aggfunc="sum"),
).reset_index(drop=False)

# unique
# [python - Create all possible combinations of multiple columns in a Pandas DataFrame - Stack Overflow](https://stackoverflow.com/questions/49980763/create-all-possible-combinations-of-multiple-columns-in-a-pandas-dataframe#58903268)

columns_required = ["year", "shotspotter_alert"]
uniques = [df_summary[i].unique().tolist() for i in columns_required ]
combinations_df = pd.DataFrame(product(*uniques), columns = columns_required)


full_combinations_df = pd.merge(
    combinations_df,
    df_summary,
    on = columns_required,
    how = "right"
).assign(
    shell_casings = lambda x: x.shell_casings.fillna(0),
    injuries = lambda x: x.injuries.fillna(0),
    arrests = lambda x: x.arrests.fillna(0)
)

select_year_range = sorted(full_combinations_df["year"].unique())
year_range_min = full_combinations_df["year"].min()
year_range_max = full_combinations_df["year"].max()


select_year_slider = st.sidebar.select_slider("Year range:", options=select_year_range, value=(year_range_max, year_range_min))

min_slider, max_slider = list(select_year_slider)[0], list(select_year_slider)[1]


selected_df_year = full_combinations_df[((full_combinations_df["year"] <= max_slider) & (full_combinations_df["year"] >= min_slider))]

# create tabs
tab_events, tab_shell_casing, tab_injuries, tab_arrests = st.tabs(["Events", "Shell Casings", "Injuries", "Arrests"])


df_filtered = df[((df["year"] <= max_slider) & (df["year"] >= min_slider))]

# https://stackoverflow.com/questions/29550414/how-can-i-split-a-column-of-tuples-in-a-pandas-dataframe
df_filtered[["latitude", "longitute"]] = df_filtered['LAT_LON_arcgis'].str.extract(pat = r'(-?\d+\.\d+),\s*(-?\d+\.\d+)')

# change type
df_filtered = df_filtered.assign(
    latitude = df_filtered["latitude"].astype("float"),
    longitute = df_filtered["longitute"].astype("float")
)

# Fix colour
df_filtered["colour"] = np.where(
    df_filtered["shotspotter_alert"],
    "#ff0800",
    "#00ff2a"
)

# set constant for events
df_filtered = df_filtered.assign(
    events = 1
)

with tab_events:

    col_timeseries, col_maps = st.columns(2)

    with col_timeseries:
        # tab
        st.header("Events")
        # st.dataframe(selected_df_year[['year', 'shotspotter_alert', 'event_counts']].reset_index(drop=True))
        st.line_chart(
            selected_df_year,
            x = "year",
            y = "event_counts",
            color="shotspotter_alert"
        )

    with col_maps:
        st.write("Red for an associated Shotspotter alert and Green for no shotspotter alert")
        st.map(data=df_filtered, latitude="latitude", longitude="longitute", color="colour", size='events')

with tab_shell_casing:

    col_timeseries, col_maps = st.columns(2)


    with col_timeseries:
        # tab
        st.header("Shell Casing")
        # st.dataframe(selected_df_year[['year', 'shotspotter_alert', 'shell_casings']].reset_index(drop=True))
        st.line_chart(
            selected_df_year,
            x = "year",
            y = "shell_casings",
            color="shotspotter_alert"
        )

    with col_maps:
        st.write("Red for an associated Shotspotter alert and Green for no shotspotter alert")
        st.map(data=df_filtered, latitude="latitude", longitude="longitute", color="colour", size='shell_casings')

with tab_injuries:

    col_timeseries, col_maps = st.columns(2)


    with col_timeseries:

        # tab
        st.header("Injuries")
        #st.dataframe(selected_df_year[['year', 'shotspotter_alert', 'injuries']].reset_index(drop=True))
        st.line_chart(
            selected_df_year,
            x = "year",
            y = "injuries",
            color="shotspotter_alert"
        )

    with col_maps:
        st.write("Red for an associated Shotspotter alert and Green for no shotspotter alert")
        st.map(data=df_filtered, latitude="latitude", longitude="longitute", color="colour", size='injuries')


with tab_arrests:

    col_timeseries, col_maps = st.columns(2)


    with col_timeseries:
        # tab
        st.header("Arrests")
        # st.dataframe(selected_df_year[['year', 'shotspotter_alert', 'arrests']].reset_index(drop=True))
        st.line_chart(
            selected_df_year,
            x = "year",
            y = "arrests",
            color="shotspotter_alert"
        )

    with col_maps:
        st.write("Red for an associated Shotspotter alert and Green for no shotspotter alert")
        st.map(data=df_filtered, latitude="latitude", longitude="longitute", color="colour", size='arrests')
