import streamlit as st
import json
from main import StravaClient, StravaAnalysis
import pandas as pd
import plotly.express as px
import os
import calendar

# cd /Users/valeriejones/Documents/GitHub/strava-dashboard
# streamlit run dashboard2.py

def load_data():
    private_tokens_file = '/Users/valeriejones/Documents/GitHub/strava-dashboard/private_tokens.json'
    with open(private_tokens_file, 'r') as f:
        private_tokens = json.load(f)
    strava = StravaClient(private_tokens)
    all_activities = strava.main()
    return all_activities
df = load_data()

def month_calendar(year, month):
    cal = calendar.Calendar()
    month_days = cal.monthdatescalendar(year, month)  # list of weeks, each week is list of 7 dates
    return month_days

year = 2025
month = 4
month_days = month_calendar(year, month)

st.write(f"### {calendar.month_name[month]} {year}")

# Flatten the list of dates to check for activity days
activity_days = set(df['date'])

for week in month_days:
    cols = st.columns(7)
    for i, day in enumerate(week):
        label = str(day.day)
        # Highlight days with activities
        if day in activity_days:
            # Show as clickable button with a color
            if cols[i].button(f"✅ {label}", key=str(day)):
                st.session_state['selected_date'] = day
        else:
            # Non-activity days, disable or normal button
            cols[i].button(label, key=str(day), disabled=True)

if 'selected_date' in st.session_state:
    selected_date = st.session_state['selected_date']
    st.write(f"**Selected date:** {selected_date}")

    # Filter activities on this date
    activities_on_date = df[df['date'] == selected_date]

    if not activities_on_date.empty:
        selected_activity = st.selectbox(
            "Select activity",
            options=activities_on_date['activity'].unique()
        )

        # Show details for the selected activity
        activity_detail = activities_on_date[activities_on_date['activity'] == selected_activity].iloc[0]
        st.write(f"**Activity:** {activity_detail['activity']}")
        st.write(f"**Distance (m):** {activity_detail['distance_m']}")
        st.write(f"**Moving time (min):** {activity_detail['moving_time_min']}")
    else:
        st.write("No activities found on this day.")

