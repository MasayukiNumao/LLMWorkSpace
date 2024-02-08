import sqlite3
import aiosqlite

def init_db():
    conn = sqlite3.connect('session_data.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS session_history (
        id INTEGER PRIMARY KEY,
        session_id TEXT NOT NULL,
        query TEXT NOT NULL,
        response TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()
        
def save_session_data(session_id, query, response):
    conn = sqlite3.connect('session_data.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO session_history (session_id, query, response) VALUES (?, ?, ?)
    ''', (session_id, query, response))
    conn.commit()
    conn.close()
    #print(f"Saved session data: session_id={session_id}, query={query}, response={response}")
        
def load_session_data(session_id):
    conn = sqlite3.connect('session_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT query, response FROM session_history WHERE session_id = ?', (session_id,))
    session_data = cursor.fetchall()
    conn.close()
    #print(f"Loaded session data for session_id={session_id}: {session_data}")
    return session_data
        
def delete_session_data(session_id):
    conn = sqlite3.connect('session_data.db')
    cursor = conn.cursor()
    cursor.execute('''
    DELETE FROM session_history WHERE session_id = ?
    ''', (session_id,))
    conn.commit()
    conn.close()
