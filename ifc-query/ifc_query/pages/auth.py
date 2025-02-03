import streamlit as st
import requests
import os
from dotenv import load_dotenv
import sys
sys.path.append("ifc-query")
from db import add_user

from ifc_query.logs import st_log

# Hide this page from navigation
st.set_page_config(
    page_title="User Info",
    initial_sidebar_state="expanded"
)

load_dotenv()

# GitHub OAuth configuration
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8080/auth'

@st.cache_data(ttl=15*60)
def get_user_data(access_token):
    headers = {'Authorization': f'token {access_token}'}
    response = requests.get('https://api.github.com/user', headers=headers)
    user_data = response.json()
    if user_data:
        # Store user data in database
        add_user(user_data["login"], user_data["name"])
    return user_data

def main():
        
    # Get the authorization code from the URL parameters
    query_params = st.query_params
    code = query_params.get('code')

    if code: # call is part of an authentication flow
        # Exchange the code for an access token
        token_url = 'https://github.com/login/oauth/access_token'
        data = {
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI
        }
        headers = {'Accept': 'application/json'}
        
        response = requests.post(token_url, data=data, headers=headers)
        response_json = response.json()
        
        if response.status_code != 200:
            st.error(f"Authentication failed: {response_json.get('error_description', response_json.get('error', 'Unknown error'))}")
        else:
            st.success("Successfully authenticated!")
            st.json(response_json)
            access_token = response_json.get('access_token')

            if access_token:
                st.session_state.access_token = access_token
                st.session_state.user_data = get_user_data(access_token)
                st_log('login', {'username': st.session_state.user_data['login'], 'ip': st.context.headers['User-Agent']})
                st.switch_page("main.py")
            else:
                st.json(query_params)
                st.error('Failed to obtain access token')
    else: # User went here, show them who they are
        user_data = st.session_state.user_data
        st.title("User Info")
        st.markdown(f"![]({user_data['avatar_url']}) Welcome, {user_data['name']}!")
        st.markdown(f"How's the weather in {user_data['location'].split(',',1)[0]}?")

if __name__ == '__main__':
    main() 