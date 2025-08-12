import streamlit as st
import json
from main import StravaClient, StravaAnalysis
import pandas as pd
import plotly.express as px
import os

# cd /Users/valeriejones/Documents/GitHub/strava-dashboard
# streamlit run dashboard.py

def load_data():
    private_tokens_file = '/Users/valeriejones/Documents/GitHub/strava-dashboard/private_tokens.json'
    with open(private_tokens_file, 'r') as f:
        private_tokens = json.load(f)
    strava = StravaClient(private_tokens)
    all_activities = strava.main()
    return all_activities
df = load_data()

st.title("🏋️‍♀️ Valerie's Fitness Dashboard")

all_activities = df['activity'].unique().tolist()
all_metrics = ['distance_m', 'moving_time_min']

selected_activities = st.multiselect("Select Activities", all_activities, default=all_activities)
selected_metric = st.selectbox("Select Metric", all_metrics)

if selected_activities and selected_metric:
    strava_analysis = StravaAnalysis(df)
    summary_df = strava_analysis.weekly_summary_multi(selected_activities, selected_metric)

    # Plot, each sport in a separate subplot stacked vertically
    for activity in selected_activities:
        data = summary_df[summary_df['activity'] == activity]
        if data.empty:
            st.write(f"No data for {activity}")
            continue

        fig = px.bar(data, x='week', y=f'total_{selected_metric}', title=f"{activity} - Weekly total {selected_metric}")
        st.plotly_chart(fig)

