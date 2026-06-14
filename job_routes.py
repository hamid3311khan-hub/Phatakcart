from flask import Blueprint, jsonify, render_template
from db import get_db

job_bp = Blueprint('job_bp', __name__)

# Ye API ke liye hai - JSON data dega
@job_bp.route('/api/jobs')
def api_jobs():
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY, 
                title VARCHAR(100), 
                company VARCHAR(100),
                location VARCHAR(100)
            );
        """)
        cur.execute("SELECT COUNT(*) FROM jobs;")
        if cur.fetchone()['count'] == 0:
            cur.execute("""
                INSERT INTO jobs (title, company, location) VALUES 
                ('Python Developer', 'Google', 'Bangalore'),
                ('Flask Developer', 'Meta', 'Mumbai'),
                ('Backend Engineer', 'Amazon', 'Delhi');
            """)
            db.commit()
        
        cur.execute("SELECT * FROM jobs ORDER BY id;")
        jobs_list = cur.fetchall()
        cur.close()
        return jsonify(jobs_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ye HTML page ke liye hai - tera jobs.html dikhayega
@job_bp.route('/jobs')
def jobs_page():
    return render_template('jobs.html')
