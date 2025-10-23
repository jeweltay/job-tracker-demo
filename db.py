import sqlite3
from flask import g

DATABASE = "jobscore.db"  # your database file name

def get_db():
    """Connect to the database, or return the existing connection."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close the database connection if it exists."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

