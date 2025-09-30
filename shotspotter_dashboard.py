import streamlit as st

# list pages on site
executive_summary = st.Page(
    page="website_pages/executive_summary.py", 
    title="Executive Summary", 
    icon="📝"
)

methodology_page = st.Page(
    page = "website_pages/methodology.py",
    title="Methodology",
    icon="📋"
)

alerts_evidence_page = st.Page(
    page="website_pages/alerts_vs_evidence.py", 
    title="Reports vs Alerts", 
    icon="🔍"
)

events_page = st.Page(
    page="website_pages/events.py", 
    title="Events", 
    icon="🔔"
)

casings_page = st.Page(
    page="website_pages/casings.py", 
    title="Bullet Casings", 
    icon="🔎"
)

injuries_page = st.Page(
    page="website_pages/injuries.py", 
    title="Injuries", 
    icon="🚑"
)

arrests_page = st.Page(
    page="website_pages/arrests.py", 
    title="Arrests", 
    icon="🚓"
)

download_page = st.Page(
    page="website_pages/download_csv_data.py", 
    title="Download", 
    icon="⬇️"
)

# navigation
pg = st.navigation(
    [
        methodology_page,
        executive_summary, 
        alerts_evidence_page, 
        events_page, casings_page, 
        injuries_page, arrests_page,
        download_page
    ]
)

pg.run()

st.write(
    "For more information on Shotspotter please visit [ShotspotterSounthinking Research](https://www.theblackresponsecambridge.com/shotspottersoundthinking) by [The Black Response (Cambridge, MA)](https://www.theblackresponsecambridge.com/)"
)

st.write(
    "The Source Code is located on GitHub [here](https://github.com/jarhin/Shotspotter-Streamlit-App)."
)