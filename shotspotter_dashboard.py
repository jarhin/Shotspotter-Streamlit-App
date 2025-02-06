import streamlit as st

# list pages
executive_summary = st.Page(
    page="pages/executive_summary.py", 
    title="Executive Summary", 
    icon="📝"
)

alerts_evidence_page = st.Page(
    page="pages/alerts_vs_evidence.py", 
    title="Reports vs Alerts", 
    icon="🔍"
)

events_page = st.Page(
    page="pages/events.py", 
    title="Events", 
    icon="🔔"
)

casings_page = st.Page(
    page="pages/casings.py", 
    title="Casings", 
    icon="🔎"
)

injuries_page = st.Page(
    page="pages/injuries.py", 
    title="Injuries", 
    icon="🚑"
)

arrests_page = st.Page(
    page="pages/arrests.py", 
    title="Arrests", 
    icon="🚓"
)

# navigation
pg = st.navigation(
    [
        executive_summary, alerts_evidence_page, 
        events_page, casings_page, 
        injuries_page, arrests_page
    ]
)

pg.run()

st.write(
    "For more information on Shotspotter please visit [ShotspotterSounthinking Research](https://www.theblackresponsecambridge.com/shotspottersoundthinking) by [The Black Response (Cambridge, MA)](https://www.theblackresponsecambridge.com/)"
)