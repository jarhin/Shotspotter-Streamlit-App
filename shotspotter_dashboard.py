import pandas as pd
import os
import streamlit as st

# from streamlit_dynamic_filters import DynamicFilters
from itertools import product
import numpy as np
import pydeck as pdk
import geopandas as gpd


# https://www.cambridgema.gov/Departments/cambridgepolice/News/2024/05/05232024
# one day values
my_day = 23
my_month = 5
my_year = 2024
url_daily_log = f"https://www.cambridgema.gov/Departments/cambridgepolice/News/{my_year}/{my_month:02}/{my_month:02}{my_day:02}{my_year}"


# some defaults
opacity_default = 0.5
radius_default = 50


# fetch
# df_one_day_log = pd.read_html(url_daily_log, skiprows = 1, header = 0)[0]

# column structure
# df_one_day_log.columns
# Index(['Type #  Date & Time', 'Info'], dtype='object')

# from scipy.stats import mannwhitneyu

# read file
df = pd.read_csv(
    os.path.join(
        os.path.dirname("__file__"),
        "Data/2018-2024_cambridge_shotspotter_incidents - cambridge_shotspotter_incidents_extended_geocoded.csv",
    ),
    header=0,
).rename(columns={"shell_casings": "casings"})

# read shapefile
gpd_df = gpd.read_file(
    os.path.join(os.path.dirname("__file__"), "shp/cambridge_locations.shp")
)

# initialise datframe for geodata
geo_df = pd.DataFrame()

# extract values
geo_df["lat"] = gpd_df.geometry.y
geo_df["lon"] = gpd_df.geometry.x

# set colour
# geo_df["colour"] = "#ffffff"

device_layer = pdk.Layer(
    "ScatterplotLayer",
    data=geo_df,
    get_position=["lon", "lat"],
    get_fill_color=[0, 0, 255],
    get_radius=radius_default / 2,
    opacity=0.25,
    stroked=True,
    filled=True,
    pickable=False,
)

# get coordinates from shapefile
# https://github.com/visgl/deck.gl/issues/4499#issuecomment-648991982
# geo_df['coordinates'] = gpd_df.apply(lambda row : row['geometry'].__geo_interface__['coordinates'], axis=1)

# set colour
# geo_df["colour"] = "#0044ff"

# read devices file
# assign weights column
cambridge_shotspotter = pd.read_csv(
    os.path.join(os.path.dirname("__file__"), "Data/shotspotter_data_filtered.csv"),
    header=0,
).assign(weights=1)

# change columns and clean data
df_summary = (
    df.assign(
        casings=lambda x: x.casings.fillna(0),
        injuries=lambda x: x.injuries.fillna(0),
        arrests=lambda x: x.arrests.fillna(0),
    )
    .groupby(["year", "shotspotter_alert"])
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


full_combinations_df = pd.merge(
    combinations_df, df_summary, on=columns_required, how="right"
).assign(
    casings=lambda x: x.casings.fillna(0),
    injuries=lambda x: x.injuries.fillna(0),
    arrests=lambda x: x.arrests.fillna(0),
)

select_year_range = sorted(full_combinations_df["year"].unique())
year_range_min = full_combinations_df["year"].min()
year_range_max = full_combinations_df["year"].max()


# set wide space as default
# https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config
st.set_page_config(
    page_title="Shotspotter Dashboard",
    page_icon="📊",
    layout="wide",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "https://www.theblackresponsecambridge.com/shotspottersoundthinking",
    },
)

# slider
select_year_slider = st.sidebar.select_slider(
    "Year range:", options=select_year_range, value=(year_range_max, year_range_min)
)

min_slider, max_slider = list(select_year_slider)[0], list(select_year_slider)[1]

# https://discuss.streamlit.io/t/changing-mapstyles-with-select-box/27069/2
mapstyle = st.sidebar.selectbox(
    "Choose Map Style:",
    options=["light", "dark", "road"],
    format_func=str.capitalize,
)

# filters
selected_df_year = full_combinations_df[
    (
        (full_combinations_df["year"] <= max_slider)
        & (full_combinations_df["year"] >= min_slider)
    )
]


# column names for looping
list_column_names = ["event_counts", "casings", "injuries", "arrests"]

# dictionary of variables
dict_variables_summary = {}

# rounding
default_rounding = 3

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
    dict_variables_summary["min_var_true" + "_" + my_col] = int(
        temp_agg[temp_agg["shotspotter_alert"] == True]["min_var"].values[0]
    )
    dict_variables_summary["min_var_false" + "_" + my_col] = int(
        temp_agg[temp_agg["shotspotter_alert"] == False]["min_var"].values[0]
    )
    dict_variables_summary["max_var_true" + "_" + my_col] = int(
        temp_agg[temp_agg["shotspotter_alert"] == True]["max_var"].values[0]
    )
    dict_variables_summary["max_var_false" + "_" + my_col] = int(
        temp_agg[temp_agg["shotspotter_alert"] == False]["max_var"].values[0]
    )
    dict_variables_summary["mean_var_true" + "_" + my_col] = round(
        float(temp_agg[temp_agg["shotspotter_alert"] == True]["mean_var"].values[0]),
        default_rounding,
    )
    dict_variables_summary["mean_var_false" + "_" + my_col] = round(
        float(temp_agg[temp_agg["shotspotter_alert"] == False]["mean_var"].values[0]),
        default_rounding,
    )
    dict_variables_summary["count_var_true" + "_" + my_col] = int(
        temp_agg[temp_agg["shotspotter_alert"] == True]["count_var"].values[0]
    )
    dict_variables_summary["count_var_false" + "_" + my_col] = int(
        temp_agg[temp_agg["shotspotter_alert"] == False]["count_var"].values[0]
    )
    dict_variables_summary["sum_var_true" + "_" + my_col] = int(
        temp_agg[temp_agg["shotspotter_alert"] == True]["sum_var"].values[0]
    )
    dict_variables_summary["sum_var_false" + "_" + my_col] = int(
        temp_agg[temp_agg["shotspotter_alert"] == False]["sum_var"].values[0]
    )

    # word summary for sums
    dict_variables_summary["sum_increase_decrease" + "_" + my_col] = (
        "increase"
        if dict_variables_summary["sum_var_true" + "_" + my_col]
        >= dict_variables_summary["sum_var_false" + "_" + my_col]
        else "decrease"
    )
    dict_variables_summary["sum_increase_decrease" + "_prefix_" + my_col] = (
        "an"
        if dict_variables_summary["sum_increase_decrease" + "_" + my_col] == "increase"
        else "a"
    )
    dict_variables_summary["sum_percentage_diff_" + my_col] = (
        0
        if dict_variables_summary["sum_var_false" + "_" + my_col] == 0
        else abs(
            dict_variables_summary["sum_var_false" + "_" + my_col]
            - dict_variables_summary["sum_var_true" + "_" + my_col]
        )
        / dict_variables_summary["sum_var_false" + "_" + my_col]
    )

    # summary for means
    dict_variables_summary["mean_diff_" + my_col] = float(
        dict_variables_summary["mean_var_true" + "_" + my_col]
        - dict_variables_summary["mean_var_false" + "_" + my_col]
    )
    dict_variables_summary["mean_percentage_diff_" + my_col] = float(
        0
        if dict_variables_summary["mean_var_false" + "_" + my_col] == 0
        else (
            dict_variables_summary["mean_var_true" + "_" + my_col]
            - dict_variables_summary["mean_var_false" + "_" + my_col]
        )
        / dict_variables_summary["mean_var_false" + "_" + my_col]
    )

    # summary for counts
    dict_variables_summary["count_years_" + my_col] = int(
        max(
            dict_variables_summary["count_var_true_" + my_col],
            dict_variables_summary["count_var_false_" + my_col],
        )
    )

# all counts
dict_variables_summary["count_years"] = max(
    [dict_variables_summary["count_years_" + my_col] for my_col in list_column_names]
)


# create tabs ------
tab_executive_summary, tab_events, tab_casings, tab_injuries, tab_arrests = st.tabs(
    ["Executive Summary", "Events", "Shell Casings", "Injuries", "Arrests"]
)


# apply filters to dataframe
df_filtered = df[((df["year"] <= max_slider) & (df["year"] >= min_slider))]

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


colour_lookup = {True: [255, 0, 0, 128], False: [0, 255, 0, 128]}


# Fix colours for map
df_filtered = df_filtered.assign(
    colour=np.where(df_filtered["shotspotter_alert"], "#ff0000", "#00ff00"),
    colour_map=df_filtered["shotspotter_alert"].apply(
        lambda row: colour_lookup.get(row)
    ),
)


# set constant for events
df_filtered = df_filtered.assign(events=1)

# Fix colour
selected_df_year = selected_df_year.assign(
    colour=np.where(selected_df_year["shotspotter_alert"], "#ff0000", "#00ff00")
)

# temp_year_df = selected_df_year.pivot(
#    index = "year",
#    columns="shotspotter_alert",
#    values=["event_counts", "casings", "injuries", "arrests"]
# ).sort_index()


# mann-whitney u test
# https://www.statology.org/mann-whitney-u-test-python/

# summary
# "Events", "Shell Casings", "Injuries", "Arrests"
# dict_variables_summary["sum_var_true" + my_col]
# list_column_names = ["event_counts", "casings", "injuries", "arrests"]


# common map objects
initial_viewing_state = pdk.data_utils.compute_view(
    df_filtered[["longitute", "latitude"]], view_proportion=1
)


# https://deckgl.readthedocs.io/en/latest/gallery/heatmap_layer.html#heatmaplayer


COLOR_BREWER_BLUE_SCALE = [
    [240, 249, 232],
    [204, 235, 197],
    [168, 221, 181],
    [123, 204, 196],
    [67, 162, 202],
    [8, 104, 172],
]

# we use sum since IOS has issues with floats in the browser
# https://deck.gl/docs/api-reference/aggregation-layers/heatmap-layer#limitations
shotspotter_devices_layer = pdk.Layer(
    "HeatmapLayer",
    data=cambridge_shotspotter,
    opacity=0.1,
    get_position=["lon", "lat"],
    # aggregation=pdk.types.String("SUM"),
    color_range=COLOR_BREWER_BLUE_SCALE,
    # threshold=0.05,
    get_weight="weights",
    # pickable=True
)


# helper functions for line chart
def display_linechart_viz(y_col: str, color_col: str):
    st.line_chart(selected_df_year, x="year", y=y_col, color=color_col)


# helper function for map
def hisplay_map_layer(my_radius_col: str, radius_size: int, opacity_value: float):
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


with tab_executive_summary:
    st.header("Number of Years")
    st.write(
        f"We consider {dict_variables_summary['count_years']} years of selected data."
    )
    st.subheader("Events")
    st.write(
        f"We find that a total of {dict_variables_summary['sum_var_false_event_counts']} non-Shotspotter events compared to a total of {dict_variables_summary['sum_var_true_event_counts']} Shotspotter events, which is {dict_variables_summary['sum_increase_decrease_event_counts']} {dict_variables_summary['sum_increase_decrease_prefix_event_counts']} of {dict_variables_summary['sum_percentage_diff_event_counts']:.2%} when we consider the non-Shotspotter events as the baseline."
    )
    st.subheader("Shell Casings")
    st.write(
        f"We find that a total of {dict_variables_summary['sum_var_false_casings']} shell casings during non-Shotspotter events compared to a total of {dict_variables_summary['sum_var_true_casings']} shell casings during Shotspotter events, which is {dict_variables_summary['sum_increase_decrease_casings']} {dict_variables_summary['sum_increase_decrease_prefix_casings']} of {dict_variables_summary['sum_percentage_diff_casings']:.2%} when we consider the non-Shotspotter shell casings as the baseline."
    )
    st.subheader("Injuries")
    st.write(
        f"We find that a total of {dict_variables_summary['sum_var_false_injuries']} injuries during non-Shotspotter events compared to a total of {dict_variables_summary['sum_var_true_injuries']} injuries during Shotspotter events, which is {dict_variables_summary['sum_increase_decrease_injuries']} {dict_variables_summary['sum_increase_decrease_prefix_injuries']} of {dict_variables_summary['sum_percentage_diff_injuries']:.2%} when we consider the non-Shotspotter injuries as the baseline."
    )
    st.subheader("Arrests")
    st.write(
        f"We find that a total of {dict_variables_summary['sum_var_false_arrests']} arrests during non-Shotspotter events compared to a total of {dict_variables_summary['sum_var_true_arrests']} arrests during Shotspotter events, which is {dict_variables_summary['sum_increase_decrease_arrests']} {dict_variables_summary['sum_increase_decrease_prefix_arrests']} of {dict_variables_summary['sum_percentage_diff_arrests']:.2%} when we consider the non-Shotspotter arrests as the baseline."
    )

with tab_events:
    # header
    st.header("Shotspotter Alerts")
    st.write(f"We consider the events with no alerts as the baseline.")

    # columns
    a1, a2, a3, a4, a5 = st.columns(5)
    a1.metric("No. of Yr", f"{dict_variables_summary['count_years_event_counts']}")
    a2.metric(
        "Alert: Avg. No. Events Per Yr.",
        f"{dict_variables_summary['mean_var_true_event_counts']:.2f}",
    )
    a3.metric(
        "No alert: Avg. No. of Events Per Yr.",
        f"{dict_variables_summary['mean_var_false_event_counts']:.2f}",
    )
    a4.metric(
        "Diff. in Avg. No. of Events Per Yr.",
        f"{dict_variables_summary['mean_diff_event_counts']:.2f}",
    )
    a5.metric(
        "Percent Diff. in Avg. No. of Events Per Yr.",
        f"{dict_variables_summary['mean_percentage_diff_event_counts']:.2%}",
    )

    # hypythesis
    # event_count_hypothesis = "The event counts are not equal between groups" if p_value_event_counts < 0.05 else "The event counts are equal between groups"

    # columns 2nd row
    # b1, b2 = st.columns(2)
    # b1.metric("Wilcoxon-Signed Rank Test", f"{p_value_event_counts:.2f}")
    # b2.metric("Hypothesis", f"{event_count_hypothesis}")

    # col_timeseries, col_table, col_maps = st.columns(3)
    col_timeseries, col_maps = st.columns(2)

    with col_timeseries:
        # tab
        st.header("Events Visualisations")
        st.write(
            ":red[Red]: Shotspotter alert; :green[Green]: No Shotspotter alert; and :blue[Blue]: Public Shotspotter devices."
        )
        # line_chart
        display_linechart_viz(y_col="event_counts", color_col="colour")

    # with col_table:
    #    # show table
    #   st.dataframe(temp_year_df["event_counts"])

    with col_maps:
        # chart
        st.pydeck_chart(
            pdk.Deck(
                map_style=f"{mapstyle}",  # 'light', 'dark', 'road'
                initial_view_state=initial_viewing_state,
                layers=[
                    hisplay_map_layer(
                        my_radius_col="events",
                        radius_size=radius_default,
                        opacity_value=opacity_default,
                    ),
                    device_layer,
                ],
                tooltip={"text": "{date} at {time}: {events} event(s) at {location}"},
            )
        )

        # st.map(data=df_filtered, latitude="latitude", longitude="longitute", color="colour", size='events')

with tab_casings:
    # header
    st.header("Shotspotter Alerts")
    st.write(f"We consider the events with no alerts as the baseline.")

    # columns
    a1, a2, a3, a4, a5 = st.columns(5)
    a1.metric("No. of Yr", f"{dict_variables_summary['count_years_casings']}")
    a2.metric(
        "Alert: Avg. No. Events Per Yr.",
        f"{dict_variables_summary['mean_var_true_casings']:.2f}",
    )
    a3.metric(
        "No alert: Avg. No. of Events Per Yr.",
        f"{dict_variables_summary['mean_var_false_casings']:.2f}",
    )
    a4.metric(
        "Diff. in Avg. No. of Events Per Yr.",
        f"{dict_variables_summary['mean_diff_casings']:.2f}",
    )
    a5.metric(
        "Percent Diff. in Avg. No. of Events Per Yr.",
        f"{dict_variables_summary['mean_percentage_diff_casings']:.2%}",
    )

    ## test
    # t_stat_casings, p_value_casings = wilcoxon(
    #    temp_year_df["casings"][True],
    #    temp_year_df["casings"][False]
    # )

    # hypythesis
    # casings_hypothesis = "The shell counts are not equal between groups" if p_value_casings < 0.05 else "The shell counts are equal between groups"

    # columns 2nd row
    # b1, b2 = st.columns(2)
    # b1.metric("Wilcoxon-Signed Rank Test", f"{p_value_casings:.2f}")
    # 2.metric("Hypothesis", f"{casings_hypothesis}")

    # col_timeseries, col_table, col_maps = st.columns(3)
    col_timeseries, col_maps = st.columns(2)

    with col_timeseries:
        # tab
        st.header("Shell Casings Visualisations")
        st.write(
            ":red[Red]: Shotspotter alert; :green[Green]: No Shotspotter alert; and :blue[Blue]: Public Shotspotter devices."
        )
        # st.dataframe(selected_df_year[['year', 'shotspotter_alert', 'casings']].reset_index(drop=True))

        # line_chart
        display_linechart_viz(y_col="casings", color_col="colour")

    # with col_table:
    #    # show table
    #    st.dataframe(temp_year_df["casings"])

    with col_maps:
        # chart
        st.pydeck_chart(
            pdk.Deck(
                map_style=f"{mapstyle}",  # 'light', 'dark', 'road'
                initial_view_state=initial_viewing_state,
                layers=[
                    hisplay_map_layer(
                        my_radius_col="casings",
                        radius_size=radius_default,
                        opacity_value=0.2,
                    ),
                    device_layer,
                ],
                tooltip={
                    "text": "{date} at {time}: {casings} shell casing(s) at {location}"
                },
            )
        )

        # st.map(data=df_filtered, latitude="latitude", longitude="longitute", color="colour", size='casings')

with tab_injuries:
    # header
    st.header("Shotspotter Alerts")
    st.write(f"We consider the events with no alerts as the baseline.")

    # columns
    a1, a2, a3, a4, a5 = st.columns(5)
    a1.metric("No. of Yr", f"{dict_variables_summary['count_years_injuries']}")
    a2.metric(
        "Alert: Avg. No. Events Per Yr.",
        f"{dict_variables_summary['mean_var_true_injuries']:.2f}",
    )
    a3.metric(
        "No alert: Avg. No. of Events Per Yr.",
        f"{dict_variables_summary['mean_var_false_injuries']:.2f}",
    )
    a4.metric(
        "Diff. in Avg. No. of Events Per Yr.",
        f"{dict_variables_summary['mean_diff_injuries']:.2f}",
    )
    a5.metric(
        "Percent Diff. in Avg. No. of Events Per Yr.",
        f"{dict_variables_summary['mean_percentage_diff_injuries']:.2%}",
    )

    # test
    # t_stat_injuries, p_value_injuries = wilcoxon(
    #    temp_year_df["injuries"][True],
    #    temp_year_df["injuries"][False]
    # )

    # hypythesis
    # injuries_hypothesis = "The injury counts are not equal between groups" if p_value_injuries < 0.05 else "The injury counts are equal between groups"

    # columns 2nd row
    # b1, b2 = st.columns(2)
    # b1.metric("Wilcoxon-Signed Rank Test", f"{p_value_injuries:.2f}")
    # b2.metric("Hypothesis", f"{injuries_hypothesis}")

    # col_timeseries, col_table, col_maps = st.columns(3)
    col_timeseries, col_maps = st.columns(2)

    with col_timeseries:
        # tab
        st.header("Injuries Visualisations")
        st.write(
            ":red[Red]: Shotspotter alert; :green[Green]: No Shotspotter alert; and :blue[Blue]: Public Shotspotter devices."
        )
        # st.dataframe(selected_df_year[['year', 'shotspotter_alert', 'injuries']].reset_index(drop=True))

        # line_chart
        display_linechart_viz(y_col="injuries", color_col="colour")

    # with col_table:
    ## show table
    #    st.dataframe(temp_year_df["injuries"])

    with col_maps:
        # chart
        st.pydeck_chart(
            pdk.Deck(
                map_style=f"{mapstyle}",  # 'light', 'dark', 'road'
                initial_view_state=initial_viewing_state,
                layers=[
                    hisplay_map_layer(
                        my_radius_col="injuries",
                        radius_size=radius_default,
                        opacity_value=opacity_default,
                    ),
                    device_layer,
                ],
                tooltip={"text": "{date} at {time}: {injuries} injuried at {location}"},
            )
        )

        # st.map(data=df_filtered, latitude="latitude", longitude="longitute", color="colour", size='injuries')


with tab_arrests:
    # header
    st.header("Shotspotter Alerts")
    st.write(f"We consider the events with no alerts as the baseline.")

    # columns
    a1, a2, a3, a4, a5 = st.columns(5)
    a1.metric("No. of Yr", f"{dict_variables_summary['count_years_arrests']}")
    a2.metric(
        "Alert: Avg. No. Events Per Yr.",
        f"{dict_variables_summary['mean_var_true_arrests']:.2f}",
    )
    a3.metric(
        "No alert: Avg. No. of Events Per Yr.",
        f"{dict_variables_summary['mean_var_false_arrests']:.2f}",
    )
    a4.metric(
        "Diff. in Avg. No. of Events Per Yr.",
        f"{dict_variables_summary['mean_diff_arrests']:.2f}",
    )
    a5.metric(
        "Percent Diff. in Avg. No. of Events Per Yr.",
        f"{dict_variables_summary['mean_percentage_diff_arrests']:.2%}",
    )

    # test
    # t_stat_arrests, p_value_arrests = wilcoxon(
    #    temp_year_df["arrests"][True],
    #    temp_year_df["arrests"][False]
    # )

    # hypythesis
    # arrests_hypothesis = "The arrest counts are not equal between groups" if p_value_arrests < 0.05 else "The arrest counts are equal between groups"

    # columns 2nd row
    # b1, b2 = st.columns(2)
    # b1.metric("Wilcoxon-Signed Rank Test", f"{p_value_arrests:.2f}")
    # b2.metric("Hypothesis", f"{arrests_hypothesis}")

    # col_timeseries, col_table, col_maps = st.columns(3)
    col_timeseries, col_maps = st.columns(2)

    with col_timeseries:
        # tab
        st.header("Arrests Visualisations")
        st.write(
            ":red[Red]: Shotspotter alert; :green[Green]: No Shotspotter alert; and :blue[Blue]: Public Shotspotter devices."
        )
        # st.dataframe(selected_df_year[['year', 'shotspotter_alert', 'arrests']].reset_index(drop=True))

        # line chart
        display_linechart_viz(y_col="arrests", color_col="colour")

    # with col_table:
    ## show table
    #    st.dataframe(temp_year_df["arrests"])

    with col_maps:
        # chart
        st.pydeck_chart(
            pdk.Deck(
                map_style=f"{mapstyle}",  # 'light', 'dark', 'road'
                initial_view_state=initial_viewing_state,
                layers=[
                    hisplay_map_layer(
                        my_radius_col="arrests",
                        radius_size=radius_default,
                        opacity_value=opacity_default,
                    ),
                    device_layer,
                ],
                tooltip={"text": "{date} at {time}: {arrests} arrest(s) at {location}"},
            )
        )

        # st.map(data=df_filtered, latitude="latitude", longitude="longitute", color="colour", size='arrests')
