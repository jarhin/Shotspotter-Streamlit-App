# libraries
import os
import streamlit as st


# helper imports
from utils.helper_functions import * 

# load data
# df = load_data_incidents()
df, aux_df = load_all_data()

# extract min and max for global sliders
year_range_min = df["year"].min()
year_range_max = df["year"].max()

# load combinations + years
full_combinations_df = year_alert_combinations_data_incidents()

# session state
if "data" not in st.session_state:
    st.session_state["data"] = df
if "aux_data" not in st.session_state:
    st.session_state["aux_data"] = aux_df
if "select_year_slider" not in st.session_state:
    st.session_state["select_year_slider"] = (year_range_min, year_range_max)
if "selected_df_year" not in st.session_state:
    st.session_state["selected_df_year"] = full_combinations_df
if "jurisdiction" not in st.session_state:
    st.session_state["jurisdiction"] = False

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

# global toggle 
unkeep("jurisdiction")
st.sidebar.toggle(
    "Exclude other jurisdictions (e.g. MBTA, State Police etc.)",
    key="_jurisdiction",
    on_change=keep,
    args=['jurisdiction']
)

# apply toggle
if st.session_state["jurisdiction"]:
    df = df.loc[df["exclude_other_jurisdictions"] == False]

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

st.header("Download")
st.subheader("Bridgestat Data")
st.write(
    "We offer the ability for the user to download the data in order to perform their own analysis."
)

st.markdown(
"""
You can either:
- hover the mouse on the table below and click on the "Download as CSV" icon,
- Click on the "Download data as CSV" button beneath the table.
"""
)

st.markdown('''
<style>
[data-testid="stMarkdownContainer"] ul{
    padding-left:40px;
}
</style>
''', unsafe_allow_html=True)

df_to_export = st.session_state["data"].drop(
    columns = ["Unnamed: 0", "index", "partial_address", "string_info"]
).rename(columns = {"LAT_LON_arcgis": "gps_location"})

# show dataframe
st.dataframe(df_to_export)

# Show download button for the selected frame.
# Ref.: https://docs.streamlit.io/library/api-reference/widgets/st.download_button
csv_data = df_to_export.to_csv(index=False).encode('utf-8')

st.download_button(
     label="Download data as CSV",
     data=csv_data,
     file_name='shotspotter_data.csv',
     mime='text/csv',
)