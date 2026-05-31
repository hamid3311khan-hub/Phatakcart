from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'surejob-secret-key-2026-change-this-in-production'

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect('surejob.db')
    c = conn.cursor()

    # Companies Table
    c.execute('''CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        industry TEXT,
        address TEXT,
        description TEXT,
        website TEXT,
        logo TEXT,
        founded TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Candidates Table
    c.execute('''CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Jobs Table
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        job_type TEXT,
        experience TEXT,
        location TEXT,
        openings INTEGER DEFAULT 1,
        salary TEXT,
        description TEXT,
        requirements TEXT,
        skills TEXT,
        perks TEXT,
        status TEXT DEFAULT 'Active',
        posted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies (id)
    )''')

    # Applications Table
    c.execute('''CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        candidate_id INTEGER NOT NULL,
        status TEXT DEFAULT 'Applied',
        applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id),
        FOREIGN KEY (candidate_id) REFERENCES candidates (id)
    )''')

    # Saved Jobs Table
    c.execute('''CREATE TABLE IF NOT EXISTS saved_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        candidate_id INTEGER NOT NULL,
        saved_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id),
        FOREIGN KEY (candidate_id) REFERENCES candidates (id)
    )''')

    conn.commit()
    conn.close()

init_db()

# ==================== HOME & JOB LISTING ====================
@app.route('/')
def index():
    conn = sqlite3.connect('surejob.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT j.*, c.company_name, c.logo as company_logo
                 FROM jobs j JOIN companies c ON j.company_id = c.id
                 WHERE j.status = 'Active' ORDER BY j.id DESC LIMIT
