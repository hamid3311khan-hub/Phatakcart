import os
import psycopg
from psycopg.rows import dict_row
from flask import g

def get_db():
    if 'db' not in g:
        g.db = psycopg.connect(os.environ['DATABASE_URL'], row_factory=dict_row)
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
