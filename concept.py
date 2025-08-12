import requests
import time
import json
import os

# File to store tokens
TOKEN_FILE = 'strava_tokens.json'

def save_tokens(tokens):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f)


def load_tokens():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, 'r') as f:
        return json.load(f)


def exchange_code_for_token(auth_code):
    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': auth_code,
            'grant_type': 'authorization_code'
        }
    )
    if response.status_code == 200:
        tokens = response.json()
        save_tokens(tokens)
        return tokens
    else:
        print("Error exchanging code:", response.text)
        return None


def refresh_access_token(refresh_token):
    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
    )
    if response.status_code == 200:
        tokens = response.json()
        save_tokens(tokens)
        return tokens
    else:
        print("Failed to refresh token:", response.text)
        return None


def get_valid_access_token():
    tokens = load_tokens()
    if tokens is None:
        print("No tokens found. Please provide an authorization code to exchange.\n",
              f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&approval_prompt=auto&scope=activity:read_all")
        auth_code = input("Enter your authorization code: ").strip()
        tokens = exchange_code_for_token(auth_code)
        if tokens is None:
            raise Exception("Failed to get tokens. Exiting.")

    expires_at = tokens['expires_at']
    now = int(time.time())
    if now > expires_at:
        print("Access token expired, refreshing...")
        tokens = refresh_access_token(tokens['refresh_token'])
        if tokens is None:
            raise Exception("Failed to refresh token. Exiting.")

    return tokens['access_token']


def get_activities(access_token, per_page=200):
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


def main():
    access_token = get_valid_access_token()
    activities = get_activities(access_token)
    if activities:
        for act in activities:
            name = act['name']
            dist = act['distance']  # meters
            date = act['start_date_local']
            print(f"Activity: {name}, Distance: {dist}m, Date: {date}")


if __name__ == '__main__':
    with open('private_tokens.json', 'r') as f:
        private_tokens = json.load(f)
    CLIENT_ID = private_tokens['CLIENT_ID']
    CLIENT_SECRET = private_tokens['CLIENT_SECRET']
    REDIRECT_URI = private_tokens['REDIRECT_URI']
    main()
