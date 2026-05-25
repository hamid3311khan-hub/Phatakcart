import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = 'surejob-secret-key-2024'

def get_db():
    return psycopg2.connect(os.environ['DATABASE_URL'])

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
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

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
            flash('Company Registered! 60 Din FREE Start', 'success')
            return redirect(url_for('index'))
        except psycopg2.IntegrityError:
            flash('Email already registered', 'error')
        except Exception as e:
            flash('Error ho gaya bhai', 'error')
            
    return render_template('register.html')

with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)
