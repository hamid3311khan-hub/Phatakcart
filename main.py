from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'surejob-secret-key-2026-change-this-in-production'

# Resume Upload Config
UPLOAD_FOLDER = 'static/resumes'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect('surejob.db')
    c = conn.cursor()

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

    c.execute('''CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        resume TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

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

    c.execute('''CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        candidate_id INTEGER NOT NULL,
        status TEXT DEFAULT 'Applied',
        applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id),
        FOREIGN KEY (candidate_id) REFERENCES candidates (id)
    )''')

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
                 WHERE j.status = 'Active' ORDER BY j.id DESC LIMIT 6''')
    jobs = c.fetchall()
    conn.close()
    return render_template('index.html', jobs=jobs)

@app.route('/jobs')
def jobs():
    conn = sqlite3.connect('surejob.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT j.*, c.company_name, c.logo as company_logo
                 FROM jobs j JOIN companies c ON j.company_id = c.id
                 WHERE j.status = 'Active' ORDER BY j.id DESC''')
    jobs = c.fetchall()
    conn.close()
    return render_template('jobs.html', jobs=jobs)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    conn = sqlite3.connect('surejob.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT j.*, c.company_name, c.logo as company_logo, c.id as company_id
                 FROM jobs j JOIN companies c ON j.company_id = c.id
                 WHERE j.id =?''', (job_id,))
    job = c.fetchone()
    conn.close()
    if not job:
        return "Job not found", 404

    already_applied = False
    if 'candidate_id' in session:
        conn2 = sqlite3.connect('surejob.db')
        c2 = conn2.cursor()
        c2.execute('SELECT id FROM applications WHERE job_id =? AND candidate_id =?',
                  (job_id, session['candidate_id']))
        already_applied = c2.fetchone() is not None
        conn2.close()

    return render_template('job_detail.html', job=job, already_applied=already_applied)

# ==================== CANDIDATE ROUTES ====================
@app.route('/candidate-register', methods=['GET', 'POST'])
def candidate_register():
    if request.method == 'POST':
        data = request.form
        hashed_pw = generate_password_hash(data['password'])
        conn = sqlite3.connect('surejob.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO candidates (name, email, password, phone) VALUES (?,?,?,?)',
                     (data['name'], data['email'], hashed_pw, data.get('phone')))
            candidate_id = c.lastrowid
            conn.commit()
            conn.close()
            session['candidate_id'] = candidate_id
            session['name'] = data['name']
            session['email'] = data['email']
            session['phone'] = data.get('phone')
            session['user_type'] = 'candidate'
            return redirect('/candidate-dashboard')
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('candidate_register.html', error='Email already exists')
    return render_template('candidate_register.html')

@app.route('/candidate-login', methods=['GET', 'POST'])
def candidate_login():
    if request.method == 'POST':
        data = request.form
        conn = sqlite3.connect('surejob.db')
        c = conn.cursor()
        c.execute('SELECT id, name, password, email, phone FROM candidates WHERE email =?', (data['email'],))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[2], data['password']):
            session['candidate_id'] = user[0]
            session['name'] = user[1]
            session['email'] = user[3]
            session['phone'] = user[4]
            session['user_type'] = 'candidate'
            return redirect('/candidate-dashboard')
        return render_template('candidate_login.html', error='Invalid credentials')
    return render_template('candidate_login.html')

@app.route('/candidate-dashboard')
def candidate_dashboard():
    if 'candidate_id' not in session:
        return redirect('/candidate-login')
    conn = sqlite3.connect('surejob.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM candidates WHERE id =?', (session['candidate_id'],))
    user = c.fetchone()

    c.execute('''SELECT a.*, j.title as job_title, j.location, c.company_name
                 FROM applications a
                 JOIN jobs j ON a.job_id = j.id
                 JOIN companies c ON j.company_id = c.id
                 WHERE a.candidate_id =? ORDER BY a.id DESC''', (session['candidate_id'],))
    applications = c.fetchall()
    conn.close()
    return render_template('candidate_dashboard.html', user=user, applications=applications)

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    file = request.files.get('resume')
    if not file or file.filename == '':
        flash('No file selected', 'danger')
        return redirect('/candidate-dashboard')

    if file and allowed_file(file.filename):
        filename = secure_filename(f"user_{session['candidate_id']}_{file.filename}")
        file.save(os.path
