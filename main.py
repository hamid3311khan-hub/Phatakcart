from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'surejob_secret_key_2026'

def get_db():
    conn = sqlite3.connect('surejob.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY, company_name TEXT, gst_no TEXT, 
        email TEXT UNIQUE, phone TEXT, password TEXT, 
        registered_on TEXT, plan_expiry TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY, company_id INTEGER, title TEXT, 
        location TEXT, salary TEXT, experience TEXT, 
        description TEXT, contact TEXT, posted_on TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Homepage with SEARCH 🔥
@app.route('/')
def home():
    search = request.args.get('search', '')
    conn = get_db()
    if search:
        jobs = conn.execute('''SELECT j.*, c.company_name FROM jobs j 
            JOIN companies c ON j.company_id = c.id 
            WHERE j.title LIKE ? OR j.location LIKE ? OR c.company_name LIKE ?
            ORDER BY j.id DESC''', (f'%{search}%', f'%{search}%', f'%{search}%')).fetchall()
    else:
        jobs = conn.execute('''SELECT j.*, c.company_name FROM jobs j 
            JOIN companies c ON j.company_id = c.id 
            ORDER BY j.id DESC''').fetchall()
    conn.close()
    return render_template_string(HOME_HTML, jobs=jobs, search=search)

HOME_HTML = '''
<!DOCTYPE html><html><head><title>Surejob - India ka Sabse Imaandaar Job Portal</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Arial;margin:0;background:#f5f5f5}
.header{background:#ff6b35;color:white;padding:20px;text-align:center}
.nav{display:flex;justify-content:center;gap:20px;background:#e85a2b;padding:10px}
.nav a{color:white;text-decoration:none;font-weight:bold}
.search-box{background:white;padding:15px;text-align:center}
.search-box input{width:60%;padding:12px;border:2px solid #ff6b35;border-radius:5px;font-size:16px}
.search-box button{padding:12px 20px;background:#ff6b35;color:white;border:none;border-radius:5px;font-weight:bold}
.container{max-width:800px;margin:20px auto;padding:0 15px}
.job-card{background:white;padding:20px;margin:15px 0;border-radius:10px;box-shadow:0 2px 5px rgba(0,0,0,0.1)}
.job-title{color:#ff6b35;font-size:22px;margin:0 0 10px 0}
.job-meta{color:#666;margin:5px 0}
.btn{display:inline-block;padding:10px 20px;margin:10px 10px 0 0;border-radius:5px;text-decoration:none;font-weight:bold}
.call-btn{background:#007bff;color:white}
.wa-btn{background:#25D366;color:white}
</style></head><body>
<div class="header"><h1>Surejob 🔥</h1><p>India ka Sabse Imaandaar Job Portal</p></div>
<div class="nav">
<a href="/">Jobs</a>
<a href="/login">Company Login</a>
<a href="/register">60 Din FREE</a>
</div>

<div class="search-box">
<form method="GET" action="/">
<input type="text" name="search" placeholder="Job Title ya Location dhoondo - Mumbai, Sales, Fresher..." value="{{search}}">
<button type="submit">🔍 Search</button>
</form>
</div>

<div class="container">
<h2>Latest Jobs - Bilkul FREE Apply</h2>
{% if jobs %}
{% for job in jobs %}
<div class="job-card">
<h3 class="job-title">{{job['title']}}</h3>
<p><b>Company:</b> {{job['company_name']}}</p>
<p class="job-meta">📍 Location: {{job['location']}} | 💰 Salary: {{job['salary']}}</p>
<p class="job-meta">💼 Experience: {{job['experience']}}</p>
<p class="job-meta">📅 Posted: {{job['posted_on']}}</p>
<a href="tel:{{job['contact']}}" class="btn call-btn">📞 Call Now</a>
<a href="https://wa.me/91{{job['contact']}}?text=Hi, I am interested in {{job['title']}} job posted on Surejob" class="btn wa-btn">💬 WhatsApp Apply</a>
</div>
{% endfor %}
{% else %}
<p style="text-align:center;padding:40px;">Koi job nahi mili "{{search}}" ke liye 😢</p>
{% endif %}
</div></body></html>
'''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        conn = get_db()
        try:
            reg_date = datetime.now()
            expiry = reg_date + timedelta(days=60)
            conn.execute('INSERT INTO companies (company_name,gst_no,email,phone,password,registered_on,plan_expiry) VALUES (?,?,?,?,?,?,?)',
                (data['company_name'],data['gst_no'],data['email'],data['phone'],data['password'],reg_date.strftime('%d %b %Y'),expiry.strftime('%d %b %Y')))
            conn.commit()
            return "Company Registered! 60 Din FREE Start 🔥 <a href='/login'>Login Karo</a>"
        except: return "Email already registered"
        finally: conn.close()
    return render_template_string('''<h2>Company Register - 60 Din FREE</h2>
<form method="POST">
Company Name: <input name="company_name" required><br><br>
GST No: <input name="gst_no" required><br><br>
Email: <input type="email" name="email" required><br><br>
Phone: <input name="phone" required><br><br>
Password: <input type="password" name="password" required><br><br>
<button>Register FREE</button></form>''')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        conn = get_db()
        company = conn.execute('SELECT * FROM companies WHERE email=? AND password=?',
            (request.form['email'], request.form['password'])).fetchone()
        conn.close()
        if company:
            session['company_id'] = company['id']
            session['company_name'] = company['company_name']
            return redirect(url_for('dashboard'))
        return "Wrong Email/Password"
    return render_template_string('''<h2>Company Login</h2>
<form method="POST">
Email: <input type="email" name="email" required><br><br>
Password: <input type="password" name="password" required><br><br>
<button>Login</button></form>''')

@app.route('/dashboard')
def dashboard():
    if 'company_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    company = conn.execute('SELECT * FROM companies WHERE id=?', (session['company_id'],)).fetchone()
    jobs = conn.execute('SELECT * FROM jobs WHERE company_id=? ORDER BY id DESC', (session['company_id'],)).fetchall()
    conn.close()
    return render_template_string('''
<h2>Dashboard - Welcome {{company['company_name']}}</h2>
<p>60 Din FREE Plan Active | Expiry: {{company['plan_expiry']}}</p>
<a href="/post-job"><button>+ Nayi Job Post Karo</button></a>
<h3>Aapki Posted Jobs: {{jobs|length}}</h3>
{% for job in jobs %}
<p>{{job['title']}} - {{job['location']}} | Posted: {{job['posted_on']}} 
<a href="/delete-job/{{job['id']}}" style="color:red;margin-left:10px;" onclick="return confirm('Job delete karni hai?')">❌ Delete</a>
</p>
{% endfor %}
<br><a href="/logout">Logout</a>
''', company=company, jobs=jobs)

@app.route('/post-job', methods=['GET','POST'])
def post_job():
    if 'company_id' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        conn = get_db()
        conn.execute('INSERT INTO jobs (company_id,title,location,salary,experience,description,contact,posted_on) VALUES (?,?,?,?,?,?,?,?)',
            (session['company_id'], request.form['title'], request.form['location'], request.form['salary'],
             request.form['experience'], request.form['description'], request.form['contact'], datetime.now().strftime('%d %b %Y')))
        conn.commit()
        conn.close()
        return "Job Post Ho Gayi! <a href='/dashboard'>Dashboard</a>"
    return render_template_string('''<h2>Nayi Job Post Karo - FREE</h2>
<form method="POST">
Job Title: <input name="title" required><br><br>
Location: <input name="location" required><br><br>
Salary: <input name="salary"><br><br>
Experience: <select name="experience"><option>Fresher</option><option>1-2 Years</option><option>2+ Years</option></select><br><br>
Description: <textarea name="description" required></textarea><br><br>
Contact Number: <input name="contact" required><br><br>
<button>Job Post Karo - FREE</button></form>''')

@app.route('/delete-job/<int:job_id>')
def delete_job(job_id):
    if 'company_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM jobs WHERE id=? AND company_id=?', (job_id, session['company_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
