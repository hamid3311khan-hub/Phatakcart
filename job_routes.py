from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from db import get_db

job_bp = Blueprint('job_bp', __name__)

# Table create function
def init_jobs_table():
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200),
            company VARCHAR(200),
            location VARCHAR(200),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    db.commit()
    cur.close()

# API: JSON data ke liye
@job_bp.route('/api/jobs')
def api_jobs():
    try:
        init_jobs_table()
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT COUNT(*) FROM jobs;")
        if cur.fetchone()['count'] == 0:
            cur.execute("""
                INSERT INTO jobs (title, company, location, description) VALUES
                ('Python Developer', 'Google', 'Bangalore', 'Python + Flask role'),
                ('Frontend Developer', 'Meta', 'Mumbai', 'React.js role'),
                ('Backend Engineer', 'Amazon', 'Delhi', 'Node.js + AWS role');
            """)
            db.commit()
        cur.execute("SELECT * FROM jobs ORDER BY id DESC;")
        jobs = cur.fetchall()
        cur.close()
        return jsonify(jobs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# HTML Pages ke Routes
@job_bp.route('/jobs')
def jobs_page():
    return render_template('jobs.html')

@job_bp.route('/job/<int:job_id>')
def job_detail(job_id):
    return render_template('job_detail.html', job_id=job_id)

@job_bp.route('/post-job')
def post_job():
    return render_template('post_job.html')

@job_bp.route('/manage-jobs')
def manage_jobs():
    return render_template('manage_jobs.html')

@job_bp.route('/company')
def company():
    return render_template('company.html')

@job_bp.route('/company-dashboard')
def company_dashboard():
    return render_template('company_dashboard.html')

@job_bp.route('/company-login')
def company_login():
    return render_template('company_login.html')

@job_bp.route('/company-register')
def company_register():
    return render_template('company_register.html')

@job_bp.route('/company-profile')
def company_profile():
    return render_template('company_profile.html')

@job_bp.route('/candidate-dashboard')
def candidate_dashboard():
    return render_template('candidate_dashboard.html')

@job_bp.route('/candidate-login')
def candidate_login():
    return render_template('candidate_login.html')

@job_bp.route('/candidate-register')
def candidate_register():
    return render_template('candidate_register.html')

@job_bp.route('/admin')
def admin():
    return render_template('admin.html')

@job_bp.route('/admin-login')
def admin_login():
    return render_template('admin_login.html')

@job_bp.route('/create-resume')
def create_resume():
    return render_template('create_resume.html')

@job_bp.route('/job-applications')
def job_applications():
    return render_template('job_applications.html')

@job_bp.route('/edit-job')
def edit_job():
    return render_template('edit_job.html')

@job_bp.route('/search-candidates')
def search_candidates():
    return render_template('search_candidates.html')
