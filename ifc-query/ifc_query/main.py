import sys
import os
import logging

# Add the current working directory to the Python path
sys.path.append(os.getcwd())

import streamlit as st
import requests
from dotenv import load_dotenv
from ifc_query import db

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Set the log level to DEBUG to capture all types of log messages
)


load_dotenv()

# GitHub OAuth configuration
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8080/auth'

st.set_page_config(
    page_title="GitHub Login Demo",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None

def github_login():
    github_auth_url = f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=read:user'
    st.markdown(f'<a href="{github_auth_url}" target="_self">Login with GitHub</a>', unsafe_allow_html=True)

@st.cache_data
def get_user_data(access_token):
    headers = {'Authorization': f'token {access_token}'}
    response = requests.get('https://api.github.com/user', headers=headers)
    return response.json()

def main():
    db.ensure_db_exists()
    st.title('GitHub Login Demo')
    init_session_state()

    if st.session_state.access_token is None:
        github_login()
    else:
        if st.session_state.user_data is None:
            st.session_state.user_data = get_user_data(st.session_state.access_token)
        
        user_data = st.session_state.user_data
        st.write(f"Welcome, {user_data['login']}!")
        st.write("Your GitHub profile information:")
        st.json(user_data)
        st.json(st.context.headers)
        
        if st.button('Logout'):
            st.session_state.access_token = None
            st.session_state.user_data = None
            st.rerun()

if __name__ == '__main__':
    main() 