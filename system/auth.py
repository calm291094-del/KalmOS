"""Sistema de autenticación"""
import hashlib
import time
from datetime import datetime, timedelta
from system.config import (
    ROOT_USER, ROOT_PASS, USER_USER, USER_PASS,
    SESSION_TIMEOUT, SESSIONS_FILE, load_json, save_json
)

class AuthSystem:
    def __init__(self):
        self.users = {
            ROOT_USER: {"password": ROOT_PASS, "role": "admin"},
            USER_USER: {"password": USER_PASS, "role": "user"},
        }
        self.sessions = load_json(SESSIONS_FILE, {})
    
    def authenticate(self, username, password):
        if username in self.users and self.users[username]["password"] == password:
            sid = hashlib.sha256(f"{username}{time.time()}{username}".encode()).hexdigest()
            self.sessions[sid] = {
                "username": username,
                "role": self.users[username]["role"],
                "created": datetime.now().isoformat(),
                "expires": (datetime.now() + timedelta(seconds=SESSION_TIMEOUT)).isoformat()
            }
            save_json(SESSIONS_FILE, self.sessions)
            return sid
        return None
    
    def validate_session(self, sid):
        if sid in self.sessions:
            s = self.sessions[sid]
            if datetime.now() < datetime.fromisoformat(s["expires"]):
                return s
            del self.sessions[sid]
            save_json(SESSIONS_FILE, self.sessions)
        return None
    
    def logout(self, sid):
        if sid in self.sessions:
            del self.sessions[sid]
            save_json(SESSIONS_FILE, self.sessions)
            return True
        return False

auth_system = AuthSystem()