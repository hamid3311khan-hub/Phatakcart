from flask import Flask, render_template_string, request, redirect, session
import sqlite3
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", 'surejob_v3_2026_final')

def get_db():
    conn = sqlite3.connect('surejob.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY, company_name TEXT, email TEXT UNIQUE, phone TEXT, password TEXT, registered_on TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS candidates (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, phone TEXT, password TEXT, registered_on TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, company_id INTEGER, title TEXT, location TEXT, salary TEXT, category TEXT, description TEXT, posted_on TEXT, views INTEGER DEFAULT 0)")
    conn.execute("CREATE TABLE IF NOT EXISTS applications (id INTEGER PRIMARY KEY, job_id INTEGER, name TEXT, email TEXT, phone TEXT, applied_on TEXT, status TEXT DEFAULT 'New')")
    conn.commit()
    conn.close()

init_db()

BASE_HTML = '''
<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SureJob</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head><body>
<nav class="navbar navbar-dark bg-primary">
<div class="container">
<a class="navbar-brand fw-bold" href="/">SureJob</a>
<div>
{% if session.candidate_id %}
<a class="btn btn-light btn-sm" href="/candidate-dashboard">{{ session.candidate_name }}</a>
<a class="btn btn-outline-light btn-sm" href="/logout">Logout</a>
{% elif session.company_id %}
<a class="btn btn-light btn-sm" href="/company-dashboard">{{ session.company_name }}</a>
<a class="btn btn-outline-light btn-sm" href="/logout">Logout</a>
{% else %}
<a class="btn btn-light btn-sm" href="/candidate-login">Candidate</a>
<a class="btn btn-outline-light btn-sm" href="/company-login">Company</a>
{% endif %}
</div></div></nav>
<div class="container my-4">{{ content|safe }}</div>
</body></html>
'''

@app.route('/')
def home():
    conn = get_db()
    jobs = conn.execute('SELECT j.*, c.company_name FROM jobs j LEFT JOIN companies c ON j.company_id = c.id ORDER BY j.id DESC LIMIT 20').fetchall()
    conn.close()
    job_cards = ""
    for job in jobs:
        job_cards += f'''
        <div class="col-md-6 mb-3">
        <div class="card"><div class="card-body">
        <h5 class="card-title">{job['title']}</h5>
        <h6 class="card-subtitle mb-2 text-muted">{job['company_name'] or 'Company'} - {job['location']}</h6>
        <p class="card-text">{job['salary']} | {job['category']}</p>
        <a href="/job/{job['id']}" class="btn btn-primary btn-sm">View & Apply</a>
        </div></div></div>'''
    content = f'<h3>Latest Jobs</h3><div class="row">{job_cards}</div>' if jobs else '<div class="alert alert-info">No jobs posted yet</div>'
    return render_template_string(BASE_HTML.replace('{{ content|safe }}', content))

@app.route('/candidate-register', methods=['GET', 'POST'])
def candidate_register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        if not all([name, email, phone, password]):
            return render_template_string(BASE_HTML.replace('{{ content|safe }}', '<div class="alert alert-danger">All fields required</div>'))
        hashed_password = generate_password_hash(password)
        conn = get_db()
        try:
            conn.execute('INSERT INTO candidates (name, email, phone, password, registered_on) VALUES (?,?,?,?,?)', (name, email, phone, hashed_password, datetime.now().strftime('%Y-%m-%d %H:%M')))
            conn.commit()
            conn.close()
            return redirect('/candidate-login')
        except:
            conn.close()
            return render_template_string(BASE_HTML.replace('{{ content|safe }}', '<div class="alert alert-danger">Email already exists</div>'))
    form = '''<div class="row justify-content-center"><div class="col-md-6">
    <h3>Candidate Registration</h3>
    <form method="post">
    <div class="mb-3"><input name="name" class="form-control" placeholder="Full Name" required></div>
    <div class="mb-3"><input name="email" type="email" class="form-control" placeholder="Email" required></div>
    <div class="mb-3"><input name="phone" class="form-control" placeholder="Phone" required></div>
    <div class="mb-3"><input name="password" type="password" class="form-control" placeholder="Password" required></div>
    <button class="btn btn-primary w-100">Register</button>
    </form></div></div>'''
    return render_template_string(BASE_HTML.replace('{{ content|safe }}', form))

@app.route('/candidate-login', methods=['GET', 'POST'])
def candidate_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        conn = get_db()
        candidate = conn.execute('SELECT * FROM candidates WHERE email=?', (email,)).fetchone()
        conn.close()
        if candidate and check_password_hash(candidate['password'], password):
            session['candidate_id'] = candidate['id']
            session['candidate_name'] = candidate['name']
            session['candidate_email'] = candidate['email']
            return redirect('/candidate-dashboard')
        return render_template_string(BASE_HTML.replace('{{ content|safe }}', '<div class="alert alert-danger">Invalid credentials</div>'))
    form = '''<div class="row justify-content-center"><div class="col-md-6">
    <h3>Candidate Login</h3>
    <form method="post">
    <div class="mb-3"><input name="email" type="email" class="form-control" placeholder="Email" required></div>
    <div class="mb-3"><input name="password" type="password" class="form-control" placeholder="Password" required></div>
    <button class="btn btn-primary w-100">Login</button>
    </form><p class="mt-3">New user? <a href="/candidate-register">Register here</a></p></div></div>'''
    return render_template_string(BASE_HTML.replace('{{ content|safe }}', form))

@app.route('/candidate-dashboard')
def candidate_dashboard():
    if 'candidate_id' not in session:
        return redirect('/candidate-login')
    conn = get_db()
    apps = conn.execute('SELECT a.*, j.title, j.location, c.company_name FROM applications a JOIN jobs j ON a.job_id = j.id LEFT JOIN companies c ON j.company_id = c.id WHERE a.email =? ORDER BY a.id DESC', (session['candidate_email'],)).fetchall()
    conn.close()
    rows = ""
    for app in apps:
        rows += f"<tr><td>{app['title']}</td><td>{app['company_name'] or ''}</td><td>{app['location']}</td><td><span class='badge bg-info'>{app['status']}</span></td></tr>"
    content = f'''<h3>Welcome {session['candidate_name']}</h3>
    <h5 class="mt-4">My Applications</h5>
    <table class="table"><thead><tr><th>Job</th><th>Company</th><th>Location</th><th>Status</th></tr></thead>
    <tbody>{rows}</tbody></table>''' if apps else f'<h3>Welcome {session["candidate_name"]}</h3><div class="alert alert-info">No applications yet</div>'
    return render_template_string(BASE_HTML.replace('{{ content|safe }}', content))

@app.route('/company-register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        if not all([company_name, email, phone, password]):
            return render_template_string(BASE_HTML.replace('{{ content|safe }}', '<div class="alert alert-danger">All fields required</div>'))
        hashed_password = generate_password_hash(password)
        conn = get_db()
        try:
            conn.execute('INSERT INTO companies (company_name, email, phone, password, registered_on) VALUES (?,?,?,?,?)', (company_name, email, phone, hashed_password, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            conn.close()
            return redirect('/company-login')
        except:
            conn.close()
            return render_template_string(BASE_HTML.replace('{{ content|safe }}', '<div class="alert alert-danger">Email already exists</div>'))
    form = '''<div class="row justify-content-center"><div class="col-md-6">
    <h3>Company Registration</h3>
    <form method="post">
    <div class="mb-3"><input name="company_name" class="form-control" placeholder="Company Name" required></div>
    <div class="mb-3"><input name="email" type="email" class="form-control" placeholder="Email" required></div>
    <div class="mb-3"><input name="phone" class="form-control" placeholder="Phone" required></div>
    <div class="mb-3"><input name="password" type="password" class="form-control" placeholder="Password" required></div>
    <button class="btn btn-primary w-100">Register</button>
    </form></div></div>'''
    return render_template_string(BASE_HTML.replace('{{ content|safe }}', form))

@app.route('/company-login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        conn = get_db()
        company = conn.execute('SELECT * FROM companies WHERE email=?', (email,)).fetchone()
        conn.close()
        if company and check_password_hash(company['password'], password):
            session['company_id'] = company['id']
            session['company_name'] = company['company_name']
            return redirect('/company-dashboard')
        return render_template_string(BASE_HTML.replace('{{ content|safe }}', '<div class="alert alert-danger">Invalid credentials</div>'))
    form = '''<div class="row justify-content-center"><div class="col-md-6">
    <h3>Company Login</h3>
    <form method="post">
    <div class="mb-3"><input name="email" type="email" class="form-control" placeholder="Email" required></div>
    <div class="mb-3"><input name="password" type="password" class="form-control" placeholder="Password" required></div>
    <button class="btn btn-primary w-100">Login</button>
    </form><p class="mt-3">New company? <a href="/company-register">Register here</a></p></div></div>'''
    return render_template_string(BASE_HTML.replace('{{ content|safe }}', form))

@app.route('/company-dashboard')
def company_dashboard():
    if 'company_id' not in session:
        return redirect('/company-login')
    conn = get_db()
    jobs = conn.execute('SELECT j.*, COUNT(a.id) as app_count FROM jobs j LEFT JOIN applications a ON j.id = a.job_id WHERE j.company_id=? GROUP BY j.id ORDER BY j.id DESC', (session['company_id'],)).fetchall()
    conn.close()
    rows = ""
    for job in jobs:
        rows += f"<tr><td>{job['title']}</td><td>{job['location']}</td><td>{job['views']}</td><td>{job['app_count']}</td><td><a href='/job-apps/{job['id']}' class='btn btn-sm btn-info'>View Apps</a></td></tr>"
    content = f'''<h3>{session['company_name']} Dashboard</h3>
    <a href="/post-job" class="btn btn-success mb-3">Post New Job</a>
    <table class="table"><thead><tr><th>Job Title</th><th>Location</th><th>Views</th><th>Applications</th><th>Action</th></tr></thead>
    <tbody>{rows}</tbody></table>''' if jobs else f'<h3>{session["company_name"]} Dashboard</h3><a href="/post-job" class="btn btn-success mb-3">Post New Job</a><div class="alert alert-info">No jobs posted yet</div>'
    return render_template_string(BASE_HTML.replace('{{ content|safe }}', content))

@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    if 'company_id' not in session:
        return redirect('/company-login')
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        location = request.form.get('location', '').strip()
        salary = request.form.get('salary', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        if not all([title, location, salary, category]):
            return render_template_string(BASE_HTML.replace('{{ content|safe }}', '<div class="alert alert-danger">Fill all required fields</div>'))
        conn = get_db()
        conn.execute('INSERT INTO jobs (company_id, title, location, salary, category, description, posted_on) VALUES (?,?,?,?,?,?,?)', (session['company_id'], title, location, salary, category, description, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        conn.close()
        return redirect('/company-dashboard')
    form = '''<div class="row justify-content-center"><div class="col-md-8">
    <h3>Post New Job</h3>
    <form method="post">
    <div class="mb-3"><input name="title" class="form-control" placeholder="Job Title" required></div>
    <div class="mb-3"><input name="location" class="form-control" placeholder="Location" required></div>
    <div class="mb-3"><input name="salary" class="form-control" placeholder="Salary e.g. 5-8 LPA" required></div>
    <div class="mb-3"><select name="category" class="form-control" required>
    <option value="">Select Category</option><option>IT Software</option><option>Sales & Marketing</option><option>BPO</option><option>HR & Admin</option><option>Other</option>
    </select></div>
    <div class="mb-3"><textarea name="description" class="form-control" rows="5" placeholder="Job Description"></textarea></div>
    <button class="btn btn-primary w-100">Post Job</button>
    </form></div></div>'''
    return render_template_string(BASE_HTML.replace('{{ content|safe }}', form))

@app.route('/job/<int:job_id>', methods=['GET', 'POST'])
def job_detail(job_id):
    conn = get_db()
    conn.execute('UPDATE jobs SET views = views + 1 WHERE id=?', (job_id,))
    conn.commit()
    job = conn.execute('SELECT j.*, c.company_name FROM jobs j LEFT JOIN companies c ON j.company_id = c.id WHERE j.id=?', (job_id,)).fetchone()
    if not job:
        conn.close()
        return redirect('/')
    if request.method == 'POST':
        if 'candidate_id' not in session:
            conn.close()
            return redirect('/candidate-login')
        name = session['candidate_name']
        email = session['candidate_email']
        phone = request.form.get('phone', '')
        conn.execute('INSERT INTO applications (job_id, name, email, phone, applied_on) VALUES (?,?,?,?,?)', (job_id, name, email, phone, datetime.now().strftime('%Y-%m-%d %H:%M')))
        conn.commit()
        conn.close()
        return render_template_string(BASE_HTML.replace('{{ content|safe }}', '<div class="alert alert-success">Applied Successfully!</div><a href="/" class="btn btn-primary">Back to Jobs</a>'))
    conn.close()
    apply_form = f'''<form method="post">
    <div class="mb-3"><input name="phone" class="form-control" placeholder="Your Phone" value="" required></div>
    <button class="btn btn-success w-100">Apply Now</button>
    </form>''' if 'candidate_id' in session else '<a href="/candidate-login" class="btn btn-primary">Login to Apply</a>'
    content = f'''<div class="row"><div class="col-md-8">
    <h3>{job['title']}</h3>
    <h5 class="text-muted">{job['company_name'] or 'Company'} - {job['location']}</h5>
    <p><b>Salary:</b> {job['salary']} | <b>Category:</b> {job['category']} | <b>Views:</b> {job['views']}</p>
    <hr><p>{job['description'] or 'No description'}</p>
    </div><div class="col-md-4"><div class="card"><div class="card-body">
    <h5>Apply for this Job</h5>{apply_form}
    </div></div></div></div>'''
    return render_template_string(BASE_HTML.replace('{{ content|safe }}', content))

@app.route('/job-apps/<int:job_id>')
def job_apps(job_id):
    if 'company_id' not in session:
        return redirect('/company-login')
    conn = get_db()
    job = conn.execute('SELECT * FROM jobs WHERE id=? AND company_id=?', (job_id, session['company_id'])).fetchone()
    if not job:
        conn.close()
        return redirect('/company-dashboard')
    apps = conn.execute('SELECT * FROM applications WHERE job_id=? ORDER BY id DESC', (job_id,)).fetchall()
    conn.close()
    rows = ""
    for app in apps:
        rows += f"<tr><td>{app['name']}</td><td>{app['email']}</td><td>{app['phone']}</td><td>{app['applied_on']}</td><td>{app['status']}</td></tr>"
    content = f'''<h3>Applications for: {job['title']}</h3>
    <a href="/company-dashboard" class="btn btn-secondary btn-sm mb-3">Back</a>
    <table class="table"><thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Applied On</th><th>Status</th></tr></thead>
    <tbody>{rows}</tbody></table>''' if apps else f'<h3>Applications for: {job["title"]}</h3><div class="alert alert-info">No applications yet</div>'
    return render_template_string(BASE_HTML.replace('{{ content|safe }}', content))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run()
