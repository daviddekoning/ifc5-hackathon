import streamlit as st
from typing import Optional, Any
import json
from datetime import datetime, timedelta
import base64
from cryptography.fernet import Fernet
import hashlib

class EncryptedCookieManager:
    def __init__(self, prefix: str, password: str):
        """
        Initialize the cookie manager with a prefix for all cookies
        and a password for encryption.
        
        Args:
            prefix (str): Prefix to add to all cookie names
            password (str): Password used for encryption
        """
        self.prefix = prefix
        # Create a Fernet key from the password
        key = hashlib.sha256(password.encode()).digest()
        self.fernet = Fernet(base64.urlsafe_b64encode(key))

    def _get_cookie_name(self, name: str) -> str:
        """Get the full cookie name with prefix"""
        return f"{self.prefix}{name}"

    def set(self, name: str, value: Any, expires_days: int = 30) -> None:
        """
        Set a cookie with an encrypted value
        
        Args:
            name (str): Cookie name
            value (Any): Value to store (will be JSON serialized)
            expires_days (int): Number of days until cookie expires
        """
        expires = datetime.now() + timedelta(days=expires_days)
        data = {
            'value': value,
            'expires': expires.isoformat()
        }
        encrypted = self.fernet.encrypt(json.dumps(data).encode())
        st.session_state[self._get_cookie_name(name)] = encrypted.decode()

    def get(self, name: str) -> Optional[Any]:
        """
        Get a cookie value, returns None if cookie doesn't exist
        or is expired
        
        Args:
            name (str): Cookie name
            
        Returns:
            Optional[Any]: Decrypted cookie value or None
        """
        cookie_name = self._get_cookie_name(name)
        if cookie_name not in st.session_state:
            return None
            
        try:
            encrypted = st.session_state[cookie_name].encode()
            decrypted = self.fernet.decrypt(encrypted)
            data = json.loads(decrypted)
            
            # Check expiration
            expires = datetime.fromisoformat(data['expires'])
            if expires < datetime.now():
                self.delete(name)
                return None
                
            return data['value']
        except Exception:
            return None

    def delete(self, name: str) -> None:
        """
        Delete a cookie
        
        Args:
            name (str): Cookie name
        """
        cookie_name = self._get_cookie_name(name)
        if cookie_name in st.session_state:
            del st.session_state[cookie_name] 