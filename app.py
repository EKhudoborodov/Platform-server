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
    return render_template('sign_in.html', username=0, password=0)

@app.route('/signin/', methods=['POST'])
def signin():
    #if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')
    if username != '' or password != '':
        cursor.execute(f"SELECT * FROM public.users WHERE login='{username}' AND password='{password}'", (str(username), str(password)))
        records = list(cursor.fetchall())
        if records != []:
            session['login'] = username
            return redirect(url_for('.home', username=username))
        else:
            return render_template('sign_in.html', username=username, password=password, no_user=1)
    else:
        return render_template('sign_in.html', username=username, password=password)
        
@app.route('/signup/', methods=['GET'])
def first():
    return render_template('sign_up.html', fullname = 0, username = 0, password1 = 0, password2 = 0)

@app.route('/signup/', methods=['POST'])
def signup():
    fullname = request.form.get('fullname')
    username = request.form.get('username')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    cursor.execute(f"SELECT * FROM public.users WHERE login='{username}'", (str(username)))
    records = list(cursor.fetchall())
    if fullname != '':
        if username != '':
            if(records == []):
                if password1 != '' and password2 != '':
                    if password1 == password2:
                        cursor.execute(f"INSERT INTO public.users (login, password, fullname, banned) VALUES ('{username}', '{password1}', '{fullname}', {False})")
                        conn.commit()
                        return redirect('http://127.0.0.1:5000/signin')
                    else:
                        return render_template('sign_up.html', fullname=fullname, username=username, password1=password1, password2=password2, defferent=1)
                else:
                    return render_template('sign_up.html', fullname=fullname, username=username, password1=password1, password2=password2)
            else:
                return render_template('sign_up.html', fullname=fullname, username=username, user_exist=1)
        else:
            return render_template('sign_up.html', fullname=fullname, username=username)
    else:
        return render_template('sign_up.html', fullname=fullname)

@app.route("/home/", methods=['GET', 'POST'])
def home():
    username = session.get('login')
    if username != None:
        return render_template('approved.html', login=f"Your login:{username}")
    else: 
        return redirect('http://127.0.0.1:5000/signin')

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run()