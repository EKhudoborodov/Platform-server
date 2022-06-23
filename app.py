import requests, os
from flask import Flask, render_template, request, redirect, url_for, session
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
def signin():
    #if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')
    session['login'] = username
    if username != '' or password != '':
        cursor.execute(f"SELECT * FROM public.users WHERE login='{username}' AND password='{password}'", (str(username), str(password)))
        records = list(cursor.fetchall())
        if records != []:
            return redirect(url_for('.home', username=username))
        else:
            return render_template('sign_in2.html')
    else:
        return render_template('sign_in1.html')
        
@app.route('/signup/', methods=['GET'])
def first():
    return render_template('sign_up.html')

@app.route('/signup/', methods=['POST'])
def signup():
    username = request.form.get('username')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    cursor.execute(f"SELECT * FROM public.users WHERE login='{username}'", (str(username)))
    records = list(cursor.fetchall())
    if username != '':
        if(records == []):
            if password1 != '' and password2 != '':
                if password1 == password2:
                    cursor.execute(f"INSERT INTO public.users (login, password, role) VALUES ('{username}', '{password1}', 'reader')")
                    conn.commit()
                    return redirect('http://127.0.0.1:5000/signin')
                else:
                    return render_template('sign_up3.html')
            else:
                return render_template('sign_up2.html')
        else:
            return render_template('sign_up4.html')
    else:
        return render_template('sign_up1.html')

@app.route("/home/", methods=['GET', 'POST'])
def home():
    username = session.get('login')
    return render_template('approved.html', login=f"Your login:{username}")

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run()