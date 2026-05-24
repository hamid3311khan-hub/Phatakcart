from flask import Flask, request, redirect, session
import sqlite3
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'surejob_2026_hamid')

def init_db():
    os.makedirs('/tmp', exist_ok=True)
    conn = sqlite3.connect('/tmp/surejob.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employers
                 (id INTEGER PRIMARY KEY, company_name TEXT, email TEXT,
                  password TEXT, start_date DATE, end_date DATE)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return '''
    <h1>Surejob - Sure Shot Jobs 🔥</h1>
    <h2>60 Din FREE Trial For Companies</h2>
    <a href="/signup"><button style="padding:15px;font-size:18px">Company Register - FREE</button></a><br><br>
    <a href="/login">Employer Login</a>
    '''

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        company = request.form['company_name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=60)
        conn = sqlite3.connect('/tmp/surejob.db')
        c = conn.cursor()
        c.execute("INSERT INTO employers (company_name, email, password, start_date, end_date) VALUES (?,?,?,?,?)",
                  (company, email, password, start_date, end_date))
        conn.commit()
        conn.close()
        return "<h2>✅ 60 Din Free Trial Shuru!</h2><a href='/login'>Login Karo</a>"
    return '''
    <h2>Surejob - Company Signup</h2>
    <h3>60 Din FREE TRIAL</h3>
    <form method="POST">
        Company: <input name="company_name" required><br><br>
        Email: <input name="email" type="email" required><br><br>
        Password: <input name="password" type="password" required><br><br>
        <button>Free Trial Shuru Karo</button>
    </form>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('/tmp/surejob.db')
        c = conn.cursor()
        c.execute("SELECT * FROM employers WHERE email =?", (email,))
        company = c.fetchone()
        conn.close()
        if company and check_password_hash(company[3], password):
            end_date = datetime.strptime(company[5], '%Y-%m-%d').date()
            if datetime.now().date() > end_date:
                return '''
                <h2>❌ Trial Khatam!</h2>
                <p>60 din Free Trial khatam. Surejob Gold: ₹5000/Year</p>
                <p>Call: 9999999999 - Hamid Bhai</p>
                '''
            days_left = (end_date - datetime.now().date()).days
            return f"<h2>Welcome {company[1]}!</h2><p>✅ Trial: {days_left} din baaki</p><a href='/logout'>Logout</a>"
        return "Galat Password"
    return '''
    <h2>Login</h2>
    <form method="POST">
        Email: <input name="email"><br><br>
        Password: <input name="password" type="password"><br><br>
        <button>Login</button>
    </form>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
