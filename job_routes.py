from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
import psycopg2
from psycopg2.extras import RealDictCursor
from functools import wraps
import os

job_bp = Blueprint('jobs', __name__)

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(os.environ.get('DATABASE_URL'), cursor_factory=RealDictCursor)
    return g.db

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('candidate_login'))
        return f(*args, **kwargs)
    return decorated_function

def company_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'company':
            flash('Access denied', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@job_bp.route('/jobs')
def job_list():
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    job_type = request.args.get('job_type', '')
    salary = request.args.get('salary', '')
    
    query = "SELECT j.*, u.name as company_name FROM jobs j JOIN users u ON j.company_id = u.id WHERE 1=1"
    params = []
    
    if keyword: query += " AND (j.title ILIKE %s OR j.description ILIKE %s OR j.skills_required ILIKE %s)"; params.extend([f'%{keyword}%']*3)
    if location: query += " AND j.location ILIKE %s"; params.append(f'%{location}%')
    if job_type: query += " AND j.job_type = %s"; params.append(job_type)
    if salary: query += " AND j.salary ILIKE %s"; params.append(f'%{salary}%')
    
    query += " ORDER BY j.id DESC"
    db = get_db()
    c = db.cursor()
    c.execute(query, params)
    jobs = c.fetchall()
    c.close()
    return render_template('jobs.html', jobs=jobs)

@job_bp.route('/job/<int:job_id>')
def job_detail(job_id):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT j.*, u.name as company_name, u.about as company_about FROM jobs j JOIN users u ON j.company_id = u.id WHERE j.id = %s", (job_id,))
    job = c.fetchone()
    c.close()
    if not job: return redirect(url_for('jobs.job_list'))
    return render_template('job_detail.html', job=job)

@job_bp.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply_job(job_id):
    if session['role'] != 'candidate': return redirect(url_for('index'))
    db = get_db()
    c = db.cursor()
    try:
        c.execute("INSERT INTO applications (job_id, candidate_id) VALUES (%s,%s)", (job_id, session['user_id']))
        db.commit()
        flash('Applied successfully!', 'success')
    except psycopg2.IntegrityError:
        db.rollback()
        flash('Already applied', 'error')
    finally:
        c.close()
    return redirect(url_for('jobs.job_detail', job_id=job_id))

@job_bp.route('/save-job/<int:job_id>', methods=['POST'])
@login_required
def save_job(job_id):
    if session['role'] != 'candidate': return redirect(url_for('index'))
    db = get_db()
    c = db.cursor()
    try:
        c.execute("INSERT INTO saved_jobs (candidate_id, job_id) VALUES (%s,%s)", (session['user_id'], job_id))
        db.commit()
        flash('Job saved!', 'success')
    except psycopg2.IntegrityError:
        db.rollback()
        flash('Already saved', 'error')
    finally:
        c.close()
    return redirect(url_for('jobs.job_detail', job_id=job_id))

@job_bp.route('/company/post-job', methods=['GET', 'POST'])
@login_required
@company_required
def post_job():
    if request.method == 'POST':
        db = get_db()
        c = db.cursor()
        c.execute('''INSERT INTO jobs (company_id, title, description, location, salary, job_type, skills_required, experience_required) 
                     VALUES (%s,%s,%s,%s)''',
                  (session['user_id'], request.form['title'], request.form['description'], request.form['location'],
                   request.form['salary'], request.form['job_type'], request.form['skills_required'], request.form['experience_required']))
        db.commit()
        c.close()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('column.company_dashboard'))
    return render_template('post_job.html')

@job_bp.route('/company/edit-job/<int:job_id>', methods=['GET', 'POST'])
@login_required
@company_required
def edit_job(job_id):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM jobs WHERE id = %s AND company_id = %s", (job_id, session['user_id']))
    job = c.fetchone()
    if not job:
        c.close()
        flash('Job not found', 'error')
        return redirect(url_for('column.company_dashboard'))
    
    if request.method == 'POST':
        c.execute('''UPDATE jobs SET title=%s, description=%s, location=%s, salary=%s, job_type=%s, 
                     skills_required=%s, experience_required=%s WHERE id=%s''',
                  (request.form['title'], request.form['description'], request.form['location'],
                   request.form['salary'], request.form['job_type'], request.form['skills_required'], 
                   request.form['experience_required'], job_id))
        db.commit()
        c.close()
        flash('Job updated!', 'success')
        return redirect(url_for('column.company_dashboard'))
    
    c.close()
    return render_template('edit_job.html', job=job)

@job_bp.route('/company/delete-job/<int:job_id>', methods=['POST'])
@login_required
@company_required
def delete_job(job_id):
    db = get_db()
    c = db.cursor()
    c.execute("DELETE FROM jobs WHERE id = %s AND company_id = %s", (job_id, session['user_id']))
    db.commit()
    c.close()
    flash('Job deleted', 'success')
    return redirect(url_for('column.company_dashboard'))
