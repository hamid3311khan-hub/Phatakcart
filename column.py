import sqlite3

# database.db ki jagah tere database file ka naam daal
conn = sqlite3.connect('database.db') 
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE users ADD COLUMN resume TEXT')
    conn.commit()
    print("Ho gaya! 'resume' column add ho gaya users table me.")
except sqlite3.OperationalError as e:
    print("Error:", e)
    print("Ya to column pehle se hai, ya database.db file nahi mil rahi")

conn.close()
