from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import psycopg2.extras
from db import get_db

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/jobs')
def job_list():
    db = get_db()
    c = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute("""SELECT j.*, u.name as company_name 
                 FROM jobs j 
                 JOIN users u ON j.company_id = u.id 
                 ORDER BY j.created_at DESC""")
    jobs = c.fetchall()
    c.close()
    return render_template('job_list.html', jobs=jobs)

@jobs_bp.route('/job/<int:id>')
def job_detail(id):
    db = get_db()
    c = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute("""SELECT j.*, u.name as company_name 
                 FROM jobs j 
                 JOIN users u ON j.company_id = u.id 
                 WHERE j.id = %s""", (id,))
    job = c.fetchone()
    
    if not job:
        c.close()
        return "Job not found", 404
    
    applied = False
    saved = False
    if 'user_id' in session and session.get('role') == 'candidate':
        c.execute("SELECT id FROM applications WHERE job_id=%s AND user_id=%s", (id, session['user_id']))
        applied = c.fetchone() is not None
        
        c.execute("SELECT id FROM saved_jobs WHERE job_id=%s AND user_id=%s", (id, session['user_id']))
        saved = c.fetchone() is not None
    
    c.close()
    return render_template('job_detail.html', job=job, applied=applied, saved=saved)

@jobs_bp.route('/job/<int:job_id>/apply', methods=['POST'])
def apply_job(job_id):
    if 'user_id' not in session or session.get('role') != 'candidate':
        flash('Please login as candidate to apply', 'warning')
        return redirect(url_for('auth.candidate_login'))
    
    db = get_db()
    c = db.cursor()
    try:
        c.execute("INSERT INTO applications (job_id, user_id, status, applied_at) VALUES (%s, %s, 'pending', NOW())", 
                  (job_id, session['user_id']))
        db.commit()
        flash('Applied successfully!', 'success')
    except psycopg2.IntegrityError:
        db.rollback()
        flash('You have already applied to this job', 'info')
    finally:
        c.close()
    return redirect(url_for('jobs.job_detail', id=job_id))

@jobs_bp.route('/job/<int:job_id>/save', methods=['POST'])
def save_job(job_id):
    if 'user_id' not in session or session.get('role') != 'candidate':
        flash('Please login to save jobs', 'warning')
        return redirect(url_for('auth.candidate_login'))
    
    db = get_db()
    c = db.cursor()
    try:
        c.execute("INSERT INTO saved_jobs (job_id, user_id) VALUES (%s, %s)", (job_id, session['user_id']))
        db.commit()
        flash('Job saved!', 'success')
    except psycopg2.IntegrityError:
        db.rollback()
        c.execute("DELETE FROM saved_jobs WHERE job_id=%s AND user_id=%s", (job_id, session['user_id']))
        db.commit()
        flash('Job unsaved', 'info')
    finally:
        c.close()
    return redirect(url_for('jobs.job_detail', id=job_id))
