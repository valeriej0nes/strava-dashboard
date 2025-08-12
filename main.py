import requests
import time
import json
import os
import pandas as pd
from datetime import datetime

class StravaClient:
    def __init__(self, private_tokens):
        self.CLIENT_ID = private_tokens['CLIENT_ID']
        self.CLIENT_SECRET = private_tokens['CLIENT_SECRET']
        self.REDIRECT_URI = private_tokens['REDIRECT_URI']
        self.TOKEN_FILE = 'strava_tokens.json'

    def save_tokens(self, tokens):
        with open(self.TOKEN_FILE, 'w') as f:
            json.dump(tokens, f)

    def load_tokens(self):
        if not os.path.exists(self.TOKEN_FILE):
            return None
        with open(self.TOKEN_FILE, 'r') as f:
            return json.load(f)

    def exchange_code_for_token(self, auth_code):
        response = requests.post(
            'https://www.strava.com/oauth/token',
            data={
                'client_id': self.CLIENT_ID,
                'client_secret': self.CLIENT_SECRET,
                'code': auth_code,
                'grant_type': 'authorization_code'
            }
        )
        if response.status_code == 200:
            tokens = response.json()
            self.save_tokens(tokens)
            return tokens
        else:
            print("Error exchanging code:", response.text)
            return None

    def refresh_access_token(self, refresh_token):
        response = requests.post(
            'https://www.strava.com/oauth/token',
            data={
                'client_id': self.CLIENT_ID,
                'client_secret': self.CLIENT_SECRET,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
        )
        if response.status_code == 200:
            tokens = response.json()
            self.save_tokens(tokens)
            return tokens
        else:
            print("Failed to refresh token:", response.text)
            return None

    def get_valid_access_token(self):
        tokens = self.load_tokens()
        if tokens is None:
            print("No tokens found. Please provide an authorization code to exchange.\n",
                  f"https://www.strava.com/oauth/authorize?client_id={self.CLIENT_ID}&response_type=code&redirect_uri={self.REDIRECT_URI}&approval_prompt=auto&scope=activity:read_all")
            auth_code = input("Enter your authorization code: ").strip()
            tokens = self.exchange_code_for_token(auth_code)
            if tokens is None:
                raise Exception("Failed to get tokens. Exiting.")

        expires_at = tokens['expires_at']
        now = int(time.time())
        if now > expires_at:
            print("Access token expired, refreshing...")
            tokens = self.refresh_access_token(tokens['refresh_token'])
            if tokens is None:
                raise Exception("Failed to refresh token. Exiting.")

        return tokens['access_token']

    def get_activities(self, access_token, per_page=200):
        url = 'https://www.strava.com/api/v3/athlete/activities'
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {'per_page': per_page}

        all_activities = []
        page = 1
        while True:
            params = {'per_page': per_page, 'page': page}
            response = requests.get('https://www.strava.com/api/v3/athlete/activities', headers=headers, params=params)
            page_activities = response.json()
            print(f'Fetched page {page} with {len(page_activities)} activities')
            # Stop if no more activities
            if not page_activities:
                break
            all_activities.extend(page_activities)
            page += 1

        if response.status_code == 200:
            return all_activities
        else:
            print("Failed to get activities:", response.text)
            return None

    def main(self, full=False):
        access_token = self.get_valid_access_token()
        activities = self.get_activities(access_token)
        if full is True:
            return activities
        else:
            all_activities = []
            if activities:
                for act in activities:
                    name = act['type']
                    dist = act['distance']  # meters
                    date = act['start_date_local']
                    moving_time = act['moving_time'] / 60  # minutes
                    print(f"Activity: {name}, Distance: {dist}m, Date: {date}, Moving Time: {moving_time}")
                    all_activities.append({'activity': name, 'distance_m': dist, 'date': date, 'moving_time_min': moving_time})
            return pd.DataFrame(all_activities)

class StravaAnalysis:
    def __init__(self, activities):
        self.activities = activities

    def weekly_summary_multi(self, activities, metric):
        # Filter activities
        filtered = self.activities[self.activities['activity'].isin(activities)].copy()
        filtered['week'] = pd.to_datetime(filtered['date']).dt.to_period('W').apply(lambda r: r.start_time)

        # Group and sum metric
        summary = filtered.groupby(['week', 'activity'])[metric].sum().reset_index()
        summary = summary.rename(columns={metric: f'total_{metric}'})
        return summary

if __name__ == '__main__':
    with open('private_tokens.json', 'r') as f:
        private_tokens = json.load(f)
    strava = StravaClient(private_tokens)
    acts = strava.main()
    print(acts)

with open('private_tokens.json', 'r') as f:
    private_tokens = json.load(f)
strava = StravaClient(private_tokens)
acts = strava.main()



