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
def sign_in_start():
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
            session['fullname'] = records[0][3] 
            session['user_id'] = records[0][0]
            return redirect(url_for('.home', fullname=records[0][3], user_id=records[0][0]))
        else:
            return render_template('sign_in.html', username=username, password=password, no_user=1)
    else:
        return render_template('sign_in.html', username=username, password=password)
        
@app.route('/signup/', methods=['GET'])
def sign_up_start():
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
                        cursor.execute(f"SELECT * FROM public.users WHERE login='{username}'", (str(username)))
                        records = list(cursor.fetchall())
                        cursor.execute(f"INSERT INTO public.role_user (user_id, role_id) VALUES ('{records[0][0]}', 4)")
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
    fullname = session.get('fullname')
    user_id = session.get('user_id')
    if fullname != None:
        if(user_id == 1):
            return render_template('home.html', fullname=fullname, admin = 1)
        else:
            return render_template('home.html', fullname=fullname, admin = 0)
    else: 
        return redirect('http://127.0.0.1:5000/signin')
        
@app.route("/role/", methods=['GET'])
def role_start():
    return render_template('role.html')
    
@app.route("/role/", methods=['POST'])
def update_role():
    username = request.form.get('username')
    role = request.form.get('role')
    action = request.form.get('action')
    if username != "":
        cursor.execute(f"SELECT * FROM public.users WHERE login='{username}'")
        records = list(cursor.fetchall())
        if records != []:
            user_id = records[0][0]
            cursor.execute(f"SELECT * FROM public.role_user WHERE user_id={user_id}")
            records = list(cursor.fetchall())
            if role=='reader':
                role_id = 4
            elif role=='writer':
                role_id = 3
            elif role=='moderator':
                role_id = 2
            else:
                role_id = 5
            if role_id == records[0][1]:
                return render_template('role.html', username=username, no_edits=1)
            else:
                if role_id != 5:
                    if action == 'update':
                        cursor.execute(f"UPDATE public.role_user SET role_id={role_id} WHERE user_id={user_id}")
                        conn.commit()
                        return render_template('role.html', username=username, update=1)
                    else:
                        cursor.execute(f"INSERT INTO public.role_user (user_id, role_id) VALUES ({user_id}, {role_id})")
                        conn.commit()
                        return render_template('role.html', username=username, new=1)
                else:
                    cursor.execute(f"UPDATE public.role_user SET role_id={role_id} WHERE user_id={user_id}")
                    cursor.execute(f"UPDATE public.users SET banned={True} WHERE user_id={user_id}")
                    conn.commit()
                    return render_template('role.html', username=username, ban=1)
                    
        else:
            return render_template('role.html', username=username, no_user=1)
    else:
        return render_template('role.html', username=username)

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run()