from flask import Blueprint, jsonify, g
from db import get_db

job_bp = Blueprint('job_bp', __name__)

@job_bp.route('/jobs')
def get_jobs():
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS jobs (id SERIAL PRIMARY KEY, title TEXT, company TEXT);")
        cur.execute("SELECT COUNT(*) FROM jobs;")
        count = cur.fetchone()['count']
        if count == 0:
            cur.execute("INSERT INTO jobs (title, company) VALUES ('Python Dev', 'Google'), ('Flask Dev', 'Meta');")
            db.commit()
        
        cur.execute("SELECT * FROM jobs ORDER BY id;")
        jobs = cur.fetchall()
        cur.close()
        return jsonify(jobs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
