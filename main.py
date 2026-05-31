from flask import Flask, request, render_template, redirect, url_for, session, flash, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

app = Flask(__name__)
app.secret_key = 'surejob_secret_key_123'

# Resume Upload Config
UPLOAD_FOLDER = 'static/resumes'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect('surejob.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            mobile TEXT,
            full_name TEXT,
            resume TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            company_name TEXT,
            mobile TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            location TEXT,
            salary TEXT,
            job_type TEXT,
            experience TEXT,
            openings INTEGER DEFAULT 1,
            requirements TEXT,
            skills TEXT,
            perks TEXT,
            company_id INTEGER,
            posted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            candidate_id INTEGER,
            applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs (id),
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized ✅")

def get_db_connection():
    conn = sqlite3.connect('surejob.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    try:
        conn = get_db_connection()
        jobs = conn.execute('''
            SELECT jobs.*, companies.company_name
            FROM jobs
            JOIN companies ON jobs.company_id = companies.id
            ORDER BY jobs.id DESC LIMIT 6
        ''').fetchall()
        conn.close()
        return render_template('index.html', jobs=jobs)
    except Exception as e:
        print(f"Error in home route: {e}")
        return render_template('index.html', jobs=[])

@app.route('/jobs')
def jobs():
    conn = get_db_connection()
    all_jobs = conn.execute('''
        SELECT jobs.*, companies.company_name
        FROM jobs
        JOIN companies ON jobs.company_id = companies.id
        ORDER BY jobs.id DESC
    ''').fetchall()
    conn.close()
    return render_template('jobs.html', jobs=all_jobs)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    conn = get_db_connection()
    job = conn.execute('''
        SELECT jobs.*, companies.company_name
        FROM jobs
        JOIN companies ON jobs.company_id = companies.id
        WHERE jobs.id =?
    ''', (job_id,)).fetchone()

    already_applied = False
    if 'user_id' in session and session['user_type'] == 'candidate':
        check = conn.execute('SELECT id FROM applications WHERE job_id =? AND candidate_id =?',
                           (job_id, session['user_id'])).fetchone()
        already_applied = True if check else False

    conn.close()
    return render_template('job_detail.html', job=job, already_applied=already_applied)

@app.route('/apply-job/<int:job_id>')
def apply_job(job_id):
    if 'user_id' not in session or session['user_type']!= 'candidate':
        return redirect(url_for('candidate_login'))

    conn = get_db_connection()
    candidate = conn.execute('SELECT resume FROM candidates WHERE id =?', (session['user_id'],)).fetchone()

    if not candidate['resume']:
        flash('Please upload your resume before applying', 'warning')
        conn.close()
        return redirect(url_for('candidate_dashboard'))

    existing = conn.execute('SELECT id FROM applications WHERE job_id =? AND candidate_id =?',
                          (job_id, session['user_id'])).fetchone()
    if existing:
        flash('You have already applied to this job', 'info')
    else:
        conn.execute('INSERT INTO applications (job_id, candidate_id) VALUES (?,?)',
                    (job_id, session['user_id']))
        conn.commit()
        flash('Applied successfully!', 'success')

    conn.close()
    return redirect(url_for('job_detail', job_id=job_id))

@app.route('/candidate/register', methods=['GET', 'POST'])
def candidate_register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        mobile = request.form.get('mobile')
        full_name = request.form.get('full_name')

        resume_filename = None
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename!= '' and allowed_file(file.filename):
                resume_filename = secure_filename(f"user_temp_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], resume_filename))

        conn = get_db_connection()
        try:
            cursor = conn.execute('INSERT INTO candidates (email, password, mobile, full_name, resume) VALUES (?,?,?,?,?)',
                         (email, password, mobile, full_name, resume_filename))

            if resume_filename:
                user_id = cursor.lastrowid
                new_filename = secure_filename(f"user_{user
