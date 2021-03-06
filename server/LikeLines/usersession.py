"""
Tracking of user sessions across HTTP requests.

Future features to be implemented:
 * Notion of "users" s.t. multiple sessions can be linked to a single user 
"""

from flask import session, current_app, request
from tokengen import generate_unique_token

import sys
import time


def ensure_session():
    # Don't create a session if there is no endpoint, e.g., favicon.ico
    # (Browsers don't send cookies for security reasons for favicon.ico)
    if request.endpoint is None:
        return
    
    session.permanent = True
    if 'session_id' not in session:
        print >>sys.stderr, 'Creating new session'
        session_id = generate_unique_token()
        session['session_id'] = session_id
        current_app.mongo.db.userSessions.insert(empty_session_object(session_id))
    else:
        print >>sys.stderr, 'Resuming previous session'
        session_id = session['session_id']

def empty_session_object(session_id):
    return {
        '_id':   session_id,
        'likes': {},
        'ts': time.time()
    }

def get_session_id():
    return session['session_id']

def get_serverside_session(session_id=None):
    if session_id is None:
        session_id = session['session_id']
    
    server_session = current_app.mongo.db.userSessions.find_one({'_id': session_id})
    if not server_session:
        server_session = empty_session_object(session_id)
        current_app.mongo.db.userSessions.insert(server_session)
    return current_app.mongo.db.userSessions.find_one({'_id': session_id}) or empty_session_object(session_id)

