import streamlit as st
import requests
import os
from dotenv import load_dotenv
from ifc_query.util.db import store_session
from ifc_query.logs import st_log
from streamlit_cookies_manager import EncryptedCookieManager

# Hide this page from navigation
st.set_page_config(
    page_title="User Info",
    initial_sidebar_state="expanded"
)

load_dotenv()

cookies = EncryptedCookieManager(
    prefix="ifc_query/",
    password=os.getenv('COOKIE_PASSWORD', 'default-secret-key')
)

if not cookies.ready():
    # Wait for the component to load and send us current cookies.
    st.stop()


# GitHub OAuth configuration
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8080/auth'

def main():
    # Get the authorization code from the URL parameters
    query_params = st.query_params
    code = query_params.get('code')

    if code:
        # Handle OAuth callback
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
                user_data = get_user_data(access_token)
                session_id = store_session(user_data['id'], access_token)
                
                # Only store the session ID in the cookie
                cookies['session_id'] = session_id
                cookies.save()
                
                st.session_state.access_token = access_token
                st.session_state.user_data = user_data
                st_log('login', {'username': user_data['login'], 'User-Agent': st.context.headers['User-Agent']})
            else:
                st.json(query_params)
                st.error('Failed to obtain access token')
    else:
        # Check authentication
        require_auth(lambda: st.error("Please log in first"))
        
        # Show user info
        user_data = st.session_state.user_data
        st.title("User Info")
        st.markdown(f"![]({user_data['avatar_url']}) Welcome, {user_data['name']}!")
        st.markdown(f"How's the weather in {user_data['location'].split(',',1)[0]}?")

if __name__ == '__main__':
    main() 