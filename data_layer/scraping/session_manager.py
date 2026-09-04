# data_layer/scraping/session_manager.py
import uuid
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        self.active_sessions = {}
        os.makedirs('sessions', exist_ok=True)
    
    def start_session(self, session_id=None):
        if not session_id:
            session_id = str(uuid.uuid4())[:8]
        self.active_sessions[session_id] = {'start': datetime.now()}
        return session_id
    
    def end_session(self, session_id):
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
