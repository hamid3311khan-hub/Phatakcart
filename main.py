from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            mobile TEXT,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized ✅")

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('candidate_register.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    mobile = request.form.get('mobile')
    full_name = request.form.get('full_name')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO candidates (email, password, mobile, full_name) VALUES (?, ?, ?, ?)',
                 (email, password, mobile, full_name))
    conn.commit()
    conn.close()
    
    return "Registration Successful!"

# Server start hote hi DB check karo
init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
