import pandas as pd
import os
import streamlit as st
# from streamlit_dynamic_filters import DynamicFilters
from itertools import product
from geopy.geocoders import ArcGIS
import numpy as np


# read file
df = pd.read_csv(
    os.path.join(
        os.path.dirname('__file__'), 
        "./Data/2018-2024_cambridge_shotspotter_incidents - cambridge_shotspotter_incidents_extended.csv"
        ),
        header=0 
)


# reset index for event ID
df = df.reset_index()


# helper function
def service_geocode(g_locator, address):
    location = g_locator.geocode(address)
    if location!=None:
      return (location.latitude, location.longitude)
    else:
      return np.NaN

df = df.assign(
    partial_address = df["location"] + ", Cambridge, Massachusetts"
)

geolocator_arcgis = ArcGIS()
df['LAT_LON_arcgis'] = df['partial_address'].apply(lambda x: service_geocode(geolocator_arcgis,x))

# write data
df.to_csv("Data/2018-2024_cambridge_shotspotter_incidents - cambridge_shotspotter_incidents_extended_geocoded.csv")

#
# load shotspotter device location
worldwide_shotspotter = pd.read_csv(
    os.path.join(
        os.path.dirname('__file__'),
        "Data/shotspotter_data_UPdating - shotspotter_data.csv"
        ),
        header=0
).drop(
    columns=["Unnamed: 0", "Unnamed: 4"]
).rename(columns={"Unnamed: 3": "Region"})


# clean data columns
worldwide_shotspotter = worldwide_shotspotter.assign(
    lat = pd.to_numeric(
        worldwide_shotspotter["lat"], 
        errors='coerce'
    ).astype("float"),
    lon = pd.to_numeric(
        worldwide_shotspotter["lon"], 
        errors='coerce'
    ).astype("float")
)


# TODO
# Filter devices in a box around Cambridge
# Load filtered devices to saved file to load later in shotspotter_dashboard.py


# dimensions from export from https://www.openstreetmap.org/#map=14/42.37836/-71.12720
# values
cambridge_lat_min, cambridge_lat_max = 42.35074, 42.420597, 
cambridge_lon_min, cambridge_lon_max = -71.17879, -71.04558


# filter within bounds and non-null
worldwide_shotspotter_filtered = worldwide_shotspotter[
   (
      worldwide_shotspotter["lat"] >= cambridge_lat_min
    ) & (
       worldwide_shotspotter["lat"] <= cambridge_lat_max
    ) & (
       worldwide_shotspotter["lon"] >= cambridge_lon_min
    ) & (
       worldwide_shotspotter["lon"] <= cambridge_lon_max
    ) & (
        worldwide_shotspotter["lat"].notnull()
    ) & (
        worldwide_shotspotter["lon"].notnull()
    )
]


# write data
# we remove index for convenience
worldwide_shotspotter_filtered.to_csv("Data/shotspotter_data_filtered.csv", index=False)