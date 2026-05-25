import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'surejob-secret-key-2024'

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://surejob_user:1WEg3kj7zFLhNYt61fDKhoabOPusUojd@dpg-d89tdsbbc2fs73fig2l0-a/surejob')

def get_db():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id SERIAL PRIMARY KEY,
            company_name VARCHAR(100) NOT NULL,
            gst_no VARCHAR(15),
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(15) NOT NULL,
            password VARCHAR(200) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            company_id INTEGER REFERENCES companies(id),
            title VARCHAR(100) NOT NULL,
            location VARCHAR(100) NOT NULL,
            salary VARCHAR(50),
            experience VARCHAR(50),
            description TEXT NOT NULL,
            contact_phone VARCHAR(15) NOT NULL,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT j.id, j.title, j.location, j.salary, j.experience, j.posted_at, c.company_name, j.contact_phone
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        ORDER BY j.posted_at DESC
    ''')
    jobs = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', jobs=jobs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        company_name = request.form['company_name']
        gst_no = request.form['gst_no']
        email = request.form['email']
        phone = request.form['phone']
        password = generate_password_hash(request.form['password'])
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO companies (company_name, gst_no, email, phone, password) VALUES (%s, %s, %s, %s, %s)',
                (company_name, gst_no, email, phone, password)
            )
            conn.commit()
            cur.close()
            conn.close()
            flash('Company Registered! 60 Din FREE Start 🔥', 'success')
            return redirect(url_for('login'))
        except psycopg2.IntegrityError:
            flash('Email already registered', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM companies WHERE email = %s', (email,))
        company = cur.fetchone()
        cur.close()
        conn.close()
        if company and check_password_hash(company[5], password):
            session['company_id'] = company[0]
            session['company_name'] = company[1]
            flash('Login Success! Welcome ' + company[1], 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Galat Email ya Password', 'error')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'company_id' not in session:
        flash('Pehle Login Karo', 'error')
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM jobs WHERE company_id = %s ORDER BY posted_at DESC', (session['company_id'],))
    my_jobs = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('dashboard.html', company_name=session['company_name'], my_jobs=my_jobs)

@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    if 'company_id' not in session:
        flash('Pehle Login Karo', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        location = request.form['location']
        salary = request.form['salary']
        experience = request.form['experience']
        description = request.form['description']
        contact_phone = request.form['contact_phone']

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO jobs (company_id, title, location, salary, experience, description, contact_phone) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (session['company_id'], title, location, salary, experience, description, contact_phone)
        )
        conn.commit()
        cur.close()
        conn.close()
        flash('Job Post Ho Gayi! Candidates ko dikh rahi hai 🔥', 'success')
        return redirect(url_for('dashboard'))

    return render_template('post_job.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout Ho Gaya', 'success')
    return redirect(url_for('index'))

with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)
