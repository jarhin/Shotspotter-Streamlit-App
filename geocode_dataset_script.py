import pandas as pd
import os
import streamlit as st
from streamlit_dynamic_filters import DynamicFilters
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