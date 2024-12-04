from flask import Flask, redirect, render_template, request, flash
import requests
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)


## Configuration:
#  Making database connection
def get_db_connection():
    with sqlite3.connect('msgs.db') as conn:
        conn.row_factory = sqlite3.Row
        print('DB connected!')
    return conn

# Initialize the data base:
def init_db():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS msgs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                msg TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

#Insert the messages into the data base
def msg_into_db(msg):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO msgs (msg) VALUES (?)', (msg,))
        conn.commit()

# Fetch the messages from the data base and display them
def display_msg():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM msgs ORDER BY timestamp DESC')
        rows = cur.fetchall()
    return rows

# Deleting messages from the last 30 minutes
def remove_msg():
    with get_db_connection()as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM msgs WHERE timestamp < datetime('now', '-30 minutes')")

# Sending a massage to discord server with webhook api
WEBHOOK_url = 'https://discord.com/api/webhooks/1313931709565374615/78hKkLr0pKKgqYJ_1LXOm8SP4-xkPWqne2HL5BbJjBR2c37OPqj2xysPrY9abnJT-GhL'
def send_msg_to_discord(msg):
    data = {
        "content": msg
    }
    response = requests.post(WEBHOOK_url, json=data)

    if response.status_code == 200:
        print("Message sent succsesfuly!")

    else:
        print("error")
        
    
    

## building routes

# Main home page
@app.route('/')
def home():
    return render_template('home_page.html')

# Sending messages page
@app.route('/send_message', methods= ['GET', 'POST'])
def snd_msg():
    if request.method == 'POST':
        msg = request.form['massage']
        msg_into_db(msg)
        send_msg_to_discord(msg)
        return redirect ('/')
    return render_template('send_message.html')

# Displying messages page
@app.route('/display_message', methods= ['GET'])
def display_message():
    msg = display_msg()
    return render_template('display_message.html', messages=msg)

@app.route('/delete_old_msg', methods=['GET'])
def del_old_msg():
    remove_msg()
    print("deleted!")
    return redirect ('/')
        
if __name__ == '__main__':
    init_db()  # Initialize DB when app starts
    app.run(debug=True)