import streamlit as st
import pandas as pd

# helper imports
from utils.helper_functions import * 


# filename url link info
filename_url_link_file = "./CSV/Filename URL Links/Filename URL Records.csv"

# load data
# df = load_data_incidents()
_, aux_df = load_all_data()

df_records = pd.read_csv(filename_url_link_file, header=0)

# combine data
df_records_aux = pd.merge(
    df_records, 
    aux_df, 
    on = "path", 
    how="outer"
).rename(
    columns={"page": "Pages", "date_string": "Dates", "Wayback Machine": "Web Archive Link"}
)

st.header("Methodology")

st.subheader("BridgeStat Data")
st.write("We make use of publicly availiable shootings and shots fired data as reported by Cambridge Police in the BridgeStat report.")

# original dataframe from past yearly reports
df = pd.DataFrame(
    {
        "Report": [
            "Dec. 2024", "Dec. 2024", 
            "Dec. 2023", 
            "Dec. 2022", "Dec. 2022",
            "Dec. 2021", "Dec. 2021",
            "Dec. 2020",
            "Dec. 2019",
            "Dec. 2018", "Dec. 2018"
        ],
        
        "Dates": [
            "1.1.24 - 6.30.24", "7.1.24 - 12.31.24",
            "1.1.23 - 12.31.23", 
            "1.1.22 - 6.30.22", "7.1.22 - 12.31.22",
            "1.1.21 - 6.31.21", "7.1.21 - 12.31.21",
            "1.1.20 - 12.28.20",
            "1.1.19 - 12.30.19",
            "1.1.18 - 7.31.18", "8.1.18 - 12.31.18"
        ],

        "Webpage": [
            "https://www.cambridgema.gov/Departments/cambridgepolice/Publications/2025/bridgestatdecember2024",
            "https://www.cambridgema.gov/Departments/cambridgepolice/Publications/2025/bridgestatdecember2024",
            "https://www.cambridgema.gov/Departments/cambridgepolice/Publications/2023/bridgestatdecember2023",
            "https://www.cambridgema.gov/Departments/cambridgepolice/Publications/2023/bridgestatdecember2022",
            "https://www.cambridgema.gov/Departments/cambridgepolice/Publications/2023/bridgestatdecember2022",
            "https://www.cambridgema.gov/Departments/cambridgepolice/Publications/2021/12/bridgestatdecember2021",
            "https://www.cambridgema.gov/Departments/cambridgepolice/Publications/2021/12/bridgestatdecember2021",
            "https://www.cambridgema.gov/Departments/cambridgepolice/Publications/2020/12/bridgestat%E2%80%93december2020",
            "https://www.cambridgema.gov/Departments/cambridgepolice/Publications/2019/12/bridgestatdecember2019",
            "https://www.cambridgema.gov/Departments/cambridgepolice/Publications/2018/12/bridgestatdecember2018",
            "https://www.cambridgema.gov/Departments/cambridgepolice/Publications/2018/12/bridgestatdecember2018"
        ],

        "PDF URL": [
            "https://www.cambridgema.gov/-/media/Files/policedepartment/BridgeStat/BridgeStat_December2024_FINAL.pdf",
            "https://www.cambridgema.gov/-/media/Files/policedepartment/BridgeStat/BridgeStat_December2024_FINAL.pdf",
            "https://www.cambridgema.gov/-/media/Files/policedepartment/BridgeStat/BridgeStat_December2023_FINAL.pdf",
            "https://www.cambridgema.gov/-/media/Files/policedepartment/BridgeStat/BridgeStat_December2022Prelim_FINAL.pdf",
            "https://www.cambridgema.gov/-/media/Files/policedepartment/BridgeStat/BridgeStat_December2022Prelim_FINAL.pdf",
            "https://www.cambridgema.gov/~/media/Files/policedepartment/BridgeStat/BridgeStat_December2021_FINAL",
            "https://www.cambridgema.gov/~/media/Files/policedepartment/BridgeStat/BridgeStat_December2021_FINAL",
            "https://www.cambridgema.gov/~/media/Files/policedepartment/BridgeStat/BridgeStat_December2020_FINAL",
            "https://www.cambridgema.gov/~/media/Files/policedepartment/BridgeStat/BridgeStat_Dec2019_FINAL",
            "https://www.cambridgema.gov/~/media/Files/policedepartment/BridgeStat/BridgeStat_Dec2018_FINAL",
            "https://www.cambridgema.gov/~/media/Files/policedepartment/BridgeStat/BridgeStat_Dec2018_FINAL"
        ],

        "Web Archive Link": [
            "https://web.archive.org/save/https://www.cambridgema.gov/-/media/Files/policedepartment/BridgeStat/BridgeStat_December2024_FINAL.pdf",
            "https://web.archive.org/save/https://www.cambridgema.gov/-/media/Files/policedepartment/BridgeStat/BridgeStat_December2024_FINAL.pdf",
            "https://web.archive.org/web/20240612235502/https://www.cambridgema.gov/-/media/Files/policedepartment/BridgeStat/BridgeStat_December2023_FINAL.pdf",
            "https://www.cambridgema.gov/-/media/Files/policedepartment/BridgeStat/BridgeStat_December2022Prelim_FINAL.pdf",
            "https://www.cambridgema.gov/-/media/Files/policedepartment/BridgeStat/BridgeStat_December2022Prelim_FINAL.pdf",
            "https://web.archive.org/web/20250311153550/https://www.cambridgema.gov/~/media/Files/policedepartment/BridgeStat/BridgeStat_December2021_FINAL",
            "https://web.archive.org/web/20250311153550/https://www.cambridgema.gov/~/media/Files/policedepartment/BridgeStat/BridgeStat_December2021_FINAL",
            "https://web.archive.org/web/20250311154122/https://www.cambridgema.gov/~/media/Files/policedepartment/BridgeStat/BridgeStat_December2020_FINAL",
            "https://web.archive.org/web/20250311165027/https://www.cambridgema.gov/~/media/Files/policedepartment/BridgeStat/BridgeStat_Dec2019_FINAL",
            "https://web.archive.org/web/20250311165609/https://www.cambridgema.gov/~/media/Files/policedepartment/BridgeStat/BridgeStat_Dec2018_FINAL",
            "https://web.archive.org/web/20250311165609/https://www.cambridgema.gov/~/media/Files/policedepartment/BridgeStat/BridgeStat_Dec2018_FINAL"
        ],

        "Pages": [
            9, 10,
            9, 
            10, 11, 
            10, 11, 
            11,
            13,
            13, 14
        ]
    }
)

# combine with new data
# TODO This may have to change once other yearly reports exists
# we automaticall sort by date
df_all = pd.concat(
    [df, df_records_aux], 
    axis=0
).assign(
    Report = lambda x: x["Report"].str.replace(".", ""),
    Date_Object = lambda x: pd.to_datetime(x["Report"], format="%b %Y")
).sort_values(
    by = "Date_Object",
    ascending=False,
    na_position='last'
).drop(
    columns=["path", "Date_Object"]
)

# udate table with all data
st.dataframe(
    df_all,
    hide_index=True,
    column_config={
        "Webpage": st.column_config.LinkColumn(
            "Webpage",
            display_text="link"
        ),

        "PDF URL": st.column_config.LinkColumn(
            "PDF URL",
            display_text="link"
        ),

        "Web Archive Link": st.column_config.LinkColumn(
            "Wayback Machine",
            display_text="link"
        ),
    }
)

st.subheader("Shotspotter device locations data")
st.markdown("We make use of multiple sources of publicly available information such as [Here Are the Secret Locations of ShotSpotter Gunfire Sensors  WIRED](https://www.wired.com/story/shotspotter-secret-sensor-locations-leak/) for the locations of Shotspotter devices in public locations.")

st.subheader("Thanks")
st.write("We thank the Boston University Spark Team for their help with regards to the data for this Shotspotter project.")