from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from job_routes import job_bp

app = Flask(__name__)
app.register_blueprint(job_bp)

app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']

            if user['role'] == 'company':
                return redirect(url_for('company_dashboard'))
            else:
                return redirect(url_for('jobs'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('login.html')

@app.route('/company_dashboard')
def company_dashboard():
    if 'user_id' not in session or session['role']!= 'company':
        return redirect(url_for('login'))

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE id=?", (session['user_id'],))
    company = c.fetchone()

    c.execute("SELECT j.*, (SELECT COUNT(*) FROM applications WHERE job_id=j.id) as app_count FROM jobs j WHERE company_id=? ORDER BY created_at DESC", (session['user_id'],))
    jobs = c.fetchall()

    c.execute("SELECT COUNT(*) FROM jobs WHERE company_id=?", (session['user_id'],))
    total_jobs = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM applications WHERE job_id IN (SELECT id FROM jobs WHERE company_id=?)", (session['user_id'],))
    total_apps = c.fetchone()[0]

    conn.close()

    return render_template('company_dashboard.html',
                           company=company,
                           jobs=jobs,
                           total_jobs=total_jobs,
                           total_apps=total_apps)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
