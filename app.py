import requests
from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect(database="server_db",
                        user="postgres",
                        password="postgres",
                        host="localhost",
                        port="5432")

cursor = conn.cursor()

@app.route('/signin/', methods=['GET'])
def index():
    return render_template('sign_in.html')

@app.route('/signin/', methods=['POST'])
def login():
    #if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')
    if username != '' or password != '':
        cursor.execute(f"SELECT * FROM public.users WHERE login='{username}' AND password='{password}'", (str(username), str(password)))
        records = list(cursor.fetchall())
        if records != []:
            return render_template('account.html', full_name=f"Hello, {records[0][1]}!", login=f"Your login:{username}", passw=f"Your password:{password}")
        else:
            return render_template('sign_in2.html')
    else:
        return render_template('sign_in1.html')

if __name__ == '__main__':
    app.run()