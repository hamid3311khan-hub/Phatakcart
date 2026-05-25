from flask import Flask, render_template_string, request, redirect, url_for, session, flash, send_from_directory
import sqlite3
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'surejob_v2_2026_shine_type'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024

UPLOAD_FOLDER = 'static/logos'
RESUME_FOLDER = 'static/resumes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESUME_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
JOB_CATEGORIES = ['Sales', 'Marketing', 'IT Software', 'HR', 'Finance', 'Operations', 'BPO', 'Customer Support', 'Engineering', 'Admin', 'Other']
LOCATIONS = ['Delhi', 'Mumbai', 'Bangalore', 'Hyderabad', 'Pune', 'Chennai', 'Kolkata', 'Noida', 'Gurgaon', 'Remote']
ADMIN_PASSWORD = 'surejob@admin123'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    conn = sqlite3.connect('surejob.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY, company_name TEXT, gst_no TEXT, email TEXT UNIQUE, phone TEXT, password TEXT, logo TEXT, registered_on TEXT, plan_expiry TEXT, status TEXT DEFAULT 'Active')""")
    conn.execute("""CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, company_id INTEGER, title TEXT, location TEXT, salary TEXT, experience TEXT, category TEXT, description TEXT, skills TEXT, contact TEXT, posted_on TEXT, status TEXT DEFAULT 'Active')""")
    conn.execute("""CREATE TABLE IF NOT EXISTS applications (id INTEGER PRIMARY KEY, job_id INTEGER, name TEXT, email TEXT, phone TEXT, resume TEXT, cover_letter TEXT, applied_on TEXT)""")
    conn.commit()
    conn.close()

init_db()

BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Surejob - India's Job Portal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f5f7fa; font-family: 'Segoe UI', sans-serif; }
    .navbar { background: linear-gradient(90deg, #4e54c8, #8f94fb)!important; }
    .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 0; }
    .job-card { transition: 0.3s; border: none; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .job-card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }
    .badge-skill { background: #e3f2fd; color: #1976d2; margin: 2px; }
    .footer { background: #2c3e50; color: white; padding: 30px 0; margin-top: 50px; }
    </style>
</head>
<body>
<nav class="navbar navbar-dark navbar-expand-lg">
    <div class="container">
        <a class="navbar-brand fw-bold fs-3" href="/"><i class="fas fa-briefcase"></i> Surejob</a>
        <div class="ms-auto">
            <a class="btn btn-light btn-sm me-2" href="/company-login"><i class="fas fa-building"></i> Employer</a>
            <a class="btn btn-warning btn-sm" href="/admin"><i class="fas fa-user-shield"></
