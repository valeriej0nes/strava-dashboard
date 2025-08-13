import streamlit as st
import json
from main import StravaClient, StravaAnalysis
import pandas as pd
import plotly.express as px
import os
import calendar

# cd /Users/valeriejones/Documents/GitHub/strava-dashboard
# streamlit run dashboard2.py

def load_data(full=False):
    private_tokens_file = '/Users/valeriejones/Documents/GitHub/strava-dashboard/private_tokens.json'
    with open(private_tokens_file, 'r') as f:
        private_tokens = json.load(f)
    strava = StravaClient(private_tokens)
    all_activities = strava.main(full)
    return all_activities

df = load_data()
df['date'] = pd.to_datetime(df['date']).dt.date  # Convert to date only

full_df = pd.DataFrame(load_data(full=True))

full_df['activity'] = full_df['type']
full_df['date'] = pd.to_datetime(full_df['start_date_local']).dt.date
full_df['distance_m'] = full_df['distance']
full_df['moving_time_min'] = full_df['moving_time'] / 60

full_df.fillna('-', inplace=True)


def month_calendar(year, month):
    cal = calendar.Calendar()
    return cal.monthdatescalendar(year, month)

# Let user pick year and month
st.sidebar.header("Select Month & Year")
year = st.sidebar.number_input("Year", min_value=2000, max_value=2025, value=2025, step=1)
month = st.sidebar.selectbox("Month", options=list(range(1,13)), format_func=lambda x: calendar.month_name[x])

# Generate calendar dates
month_days = month_calendar(year, month)

st.write(f"### {calendar.month_name[month]} {year}")

activity_days = set(df['date'])

for week in month_days:
    cols = st.columns(7)
    for i, day in enumerate(week):
        label = str(day.day)
        # Only enable buttons for days within the selected month
        if day.month == month:
            if day in activity_days:
                if cols[i].button(f"✅ {label}", key=str(day)):
                    st.session_state['selected_date'] = day
            else:
                cols[i].button(label, key=str(day), disabled=True)
        else:
            cols[i].button(label, key=str(day), disabled=True)  # Grey out days from other months

# Show activity details if date selected
if 'selected_date' in st.session_state:
    selected_date = st.session_state['selected_date']
    st.write(f"**Selected date:** {selected_date}")

    activities_on_date = full_df[full_df['date'] == selected_date]

    if not activities_on_date.empty:
        selected_activity = st.selectbox(
            "Select activity",
            options=activities_on_date['activity'].unique()
        )
        activity_detail = activities_on_date[activities_on_date['activity'] == selected_activity].iloc[0]

        st.title(f"{activity_detail['name']}")
        st.write(f"{activity_detail['activity']} · {round(activity_detail['distance_m'] / 1000, 1)} km · {round(activity_detail['moving_time_min'], 1)} min")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### Distance (m)")
            st.markdown(f"**{activity_detail['distance_m']}**")
            st.caption("TOTAL")

        with col2:
            st.markdown("### Time (min)")
            st.markdown(f"**{activity_detail['moving_time_min']}**")
            st.caption("MOVING")

        with col3:
            st.markdown("### Heart Rate (bpm)")
            st.markdown(f"**{activity_detail['average_heartrate']}**")
            st.caption("AVERAGE")

    else:
        st.write("No activities found on this day.")