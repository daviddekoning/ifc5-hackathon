import sys
import os
import logging

# Add the current working directory to the Python path
sys.path.append(os.getcwd())

import streamlit as st
import requests
from dotenv import load_dotenv, dotenv_values
from ifc_query.auth_helpers import require_auth
from ifc_query.db import delete_session, ensure_db_exists
from streamlit_cookies_manager  import EncryptedCookieManager

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

# Initialize cookie manager
cookies = EncryptedCookieManager(
    prefix="ifc_query/",
    password=os.getenv('COOKIE_PASSWORD', 'default-secret-key')
)
if not cookies.ready():
    # Wait for the component to load and send us current cookies.
    st.stop()

def github_login():
    github_auth_url = f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=read:user'
    st.markdown(f'<a href="{github_auth_url}" target="_self">Login with GitHub</a>', unsafe_allow_html=True)

@st.cache_data
def get_user_data(access_token):
    headers = {'Authorization': f'token {access_token}'}
    response = requests.get('https://api.github.com/user', headers=headers)
    return response.json()

def main():
    ensure_db_exists()
    st.title('GitHub Login Demo')

    # Check authentication - will stop execution if not authenticated
    require_auth(cookies, github_login)
    
    # User is authenticated at this point
    user_data = st.session_state.user_data
    st.write(f"Welcome, {user_data['login']}!")
    st.write("Your GitHub profile information:")
    st.json(user_data)
    
    if st.button('Logout'):
        session_id = cookies.get('session_id')
        if session_id:
            delete_session(session_id)
            cookies.delete('session_id')
        st.session_state.access_token = None
        st.session_state.user_data = None
        st.rerun()

if __name__ == '__main__':
    main() 