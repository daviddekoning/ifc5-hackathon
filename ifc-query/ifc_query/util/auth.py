import streamlit as st
import requests
import os
from dotenv import load_dotenv
from typing import Optional, Callable
from ifc_query.util.db import (
    add_user, get_session, delete_session
)

load_dotenv()

# Initialize cookie manager

@st.cache_data(ttl=15*60) # check with the auth server every 15 minutes
def get_user_data(access_token):
    headers = {'Authorization': f'token {access_token}'}
    response = requests.get('https://api.github.com/user', headers=headers)
    user_data = response.json()
    if user_data:
        # Store user data in database
        add_user(user_data["login"], user_data["name"])
    return user_data

def require_auth(cookies, callback: Optional[Callable] = None) -> None:
    """
    Checks if user is authenticated and sets up session data.
    If not authenticated, executes callback (if provided) and stops execution.
    
    Usage:
        require_auth(lambda: st.error("Please log in"))
    """
    # First check session state
    if 'access_token' not in st.session_state or not st.session_state.access_token:
        # Check for session cookie
        session_id = cookies.get('session_id', None)
        if session_id:
            session = get_session(session_id)
            if session:
                st.session_state.access_token = session['access_token']
                # Fetch user data if not present
                if 'user_data' not in st.session_state or not st.session_state.user_data:
                    headers = {'Authorization': f'token {session["access_token"]}'}
                    response = requests.get('https://api.github.com/user', headers=headers)
                    if response.status_code == 200:
                        st.session_state.user_data = response.json()
                    else:
                        # Token might be invalid
                        delete_session(session_id)
                        cookies.delete('session_id')
                        if callback:
                            callback()
                        st.stop()
                return
            else:
                # Invalid or expired session
                cookies.delete('session_id')
        
        # No valid session found
        if callback:
            callback()
        st.stop()
    
    # We have an access token in session state
    if 'user_data' not in st.session_state or not st.session_state.user_data:
        # Fetch user data
        headers = {'Authorization': f'token {st.session_state.access_token}'}
        response = requests.get('https://api.github.com/user', headers=headers)
        if response.status_code == 200:
            st.session_state.user_data = response.json()
        else:
            # Token is invalid
            st.session_state.access_token = None
            st.session_state.user_data = None
            if callback:
                callback()
            st.stop() 