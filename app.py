import requests, os, psycopg2, functional
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

conn = psycopg2.connect(database="server_db",
                        user="postgres",
                        password="postgres",
                        host="localhost",
                        port="5432")

cursor = conn.cursor()

"""
URL = "http://127.0.0.1:5000/"
users: {id, login, password, fullname, isbanned}
role_user: {user_id, role_id}
article: {id, name, title, description, isdeleted, date}
article_writer: {article_id, user_id, isauthor}
article_status: {article_id, status_id}
article_topic: {article_id, topic_id}
topic: {id, name}
rating: {id, user_id, article_id, date, rate, isdeleted}
"""

@app.route('/', methods=['GET', 'POST'])
def main_page():
    roles = session.get('role')
    if roles != None:
        return redirect(url_for('.home'))
    else:
        return redirect(url_for('.sign_in_start'))

@app.route('/signin/', methods=['GET'])
def sign_in_start():
    functional.stop_sessions()
    return render_template('sign_in.html')

@app.route('/signin/', methods=['POST'])
def signin():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == '' or password == '':
        return render_template('sign_in.html', username=username, password=password)
    else:
        cursor.execute(f"SELECT * FROM public.users WHERE login='{username}' AND password='{password}'", (str(username), str(password)))
        records = list(cursor.fetchall())
        if records == []:
            return render_template('sign_in.html', no_user=1)
        else:
            user_id = records[0][0]
            session['user'] = user_id
            session['fullname'] = records[0][3]
            session['ban'] = records[0][4]
            cursor.execute(f"SELECT * FROM public.role_user WHERE user_id={user_id}")
            records = list(cursor.fetchall())
            roles = functional.select_role(functional.send_roles(records))
            session['role'] = roles
            return redirect(url_for('.home'))
        
@app.route('/signup/', methods=['GET'])
def sign_up_start():
    return render_template('sign_up.html')

@app.route('/signup/', methods=['POST'])
def signup():
    fullname = request.form.get('fullname')
    username = request.form.get('username')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    cursor.execute(f"SELECT * FROM public.users WHERE login='{username}'", (str(username)))
    records = list(cursor.fetchall())
    if fullname == '':
        return render_template('sign_up.html', fullname=fullname)
    elif username == '':
        return render_template('sign_up.html', username=username)
    elif records != [] :
        return render_template('sign_up.html', user_exist=1)
    elif password1 == '' and password2 == '':
        return render_template('sign_up.html', password1=password1, password2=password2)
    elif password1 != password2:
        return render_template('sign_up.html', defferent=1)
    else:
        cursor.execute(f"INSERT INTO public.users (login, password, fullname, banned) VALUES ('{username}', '{password1}', '{fullname}', {False})")
        conn.commit()
        cursor.execute(f"SELECT * FROM public.users WHERE login='{username}'", (str(username)))
        records = list(cursor.fetchall())
        cursor.execute(f"INSERT INTO public.role_user (user_id, role_id) VALUES ('{records[0][0]}', 4)")
        conn.commit()
        return redirect(url_for('.sign_in_start'))

@app.route("/home/", methods=['GET', 'POST'])
def home():
    return functional.authorization_check(3, 'home')

@app.route("/role/", methods=['GET'])
def role_start():
    return functional.authorization_check(0, 'role')
    
@app.route("/role/", methods=['POST'])
def update_role():
    roles = session.get('role')
    new_publish = f"({functional.check_writer_uploads()})"
    ban = session.get('ban')
    username = request.form.get('username')
    role = request.form.get('role')
    action = request.form.get('action')
    if username == "":
        return render_template('role.html', username=username)
    else:
        cursor.execute(f"SELECT * FROM public.users WHERE login='{username}'")
        records = list(cursor.fetchall())
        if records == []:
            return render_template('role.html', no_user=1)
        else:
            user_id = records[0][0]
            role_id = functional.crypt_role(role)
            cursor.execute(f"SELECT * FROM public.role_user WHERE user_id={user_id} and role_id={role_id}")
            records = list(cursor.fetchall())
            if records!=[]:
                return render_template('role.html',  ban=ban, a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, no_edits=1)
            else:
                if role_id != 5:
                    if action == 'remove':
                        cursor.execute(f"DELETE FROM public.role_user WHERE user_id={user_id} and role_id={role_id}")
                        conn.commit()
                        cursor.execute(f"SELECT * FROM public.role_user WHERE user_id={user_id}")
                        records = list(cursor.fetchall())
                        if records == []:
                            cursor.execute(f"INSERT INTO public.role_user (user_id, role_id) VALUES ({user_id}, 4)")
                            conn.commit()
                        return render_template('role.html', ban=ban, a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, username=username, update=1)
                    else:
                        cursor.execute(f"INSERT INTO public.role_user (user_id, role_id) VALUES ({user_id}, {role_id})")
                        conn.commit()
                        return render_template('role.html', ban=ban, a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, username=username, new=1)
                else:
                    if action == 'remove':
                        cursor.execute(f"UPDATE public.role_user SET role_id=4 WHERE user_id={user_id} and role_id={role_id}")
                        cursor.execute(f"UPDATE public.users SET banned={False} WHERE id={user_id}")
                        conn.commit()
                        return render_template('role.html', ban=ban, a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, username=username, banned=1)
                    else:
                        cursor.execute(f"UPDATE public.role_user SET role_id={role_id} WHERE user_id={user_id}")
                        cursor.execute(f"UPDATE public.users SET banned={True} WHERE id={user_id}")
                        conn.commit()
                        return render_template('role.html', ban=ban, a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, username=username, banned=1)
                        
@app.route("/workshop/", methods=['GET'])
def workshop_start():
    roles = session.get('role')
    if roles == None:
        return redirect(url_for('.sign_in_start'))
    elif roles[0] == 1 or roles[2] == 1:
        user_id = session.get('user')
        return functional.workshop_check(user_id, roles, 0)
    else:
        return redirect(url_for('.home'))


@app.route("/workshop/", methods=['POST'])
def workshop():
    action = request.form.get('create')
    new_publish = f"({functional.check_writer_uploads()})"
    if action == 'Create new article':
        return redirect(url_for('.create'))

@app.route("/create/", methods=['GET'])
def create_start():
    return functional.authorization_check(2, 'create')

@app.route("/create/", methods=['POST'])
def create():
    roles = flask.session.get('role')
    new_publish = f"({functional.check_writer_uploads()})"
    article = request.form.get('article')
    #Check for simbols in article name
    for char in article:
        if not (char.isalpha() or char.isdigit() or cahr == " "):
            return render_template('create.html', a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, article_sim = 1)
    title = request.form.get('title')
    #Check for simbols in article's title
    for char in title:
        if not (char.isalpha() or char.isdigit() or cahr == " "):
            return render_template('create.html', a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, title_sim = 1)
    topic_id = request.form.get('topic')
    user_id = session.get('user')
    cursor.execute(f"SELECT * FROM public.article WHERE name='{article}'")
    records = list(cursor.fetchall())
    if records != []:
        return render_template('create.html', a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, article_exist = 1)
    else:
        path = f".\\articles\\{article}.txt"
        time = functional.get_current_date()
        cursor.execute(f"INSERT INTO public.article (name, title, description, isdeleted, date) VALUES ('{article}', '{title}', '{path}', {False}, '{time}')")
        conn.commit()
        cursor.execute(f"SELECT * FROM public.article WHERE name='{article}'")
        records = list(cursor.fetchall())
        cursor.execute(f"INSERT INTO public.article_status (article_id, status_id) VALUES ({records[0][0]}, 1)")
        cursor.execute(f"INSERT INTO public.article_writer (article_id, user_id, isauthor) VALUES ({records[0][0]}, {user_id}, {True})")
        cursor.execute(f"INSERT INTO public.article_topic (article_id, topic_id) VALUES ({records[0][0]}, {topic_id})")
        conn.commit()
        path = f".\\articles\\{article}.txt"
        with open(path, "w") as file:
            file.write("")
        return redirect(url_for('.draft', article_name = article))
    
@app.route("/create/<article_name>", methods=['GET'])
def draft_start(article_name):
    return functional.authorization_check_draft(article_name)
    
@app.route("/create/<article_name>", methods=['POST'])
def draft(article_name):
    roles = session.get('role')
    ban = session.get('ban')
    new_publish = f"({functional.check_writer_uploads()})"
    article_text = request.form.get('article_text')
    title = request.form.get('title')
    action = request.form.get('action')
    cursor.execute(f"SELECT * FROM public.article WHERE name='{article_name}'")
    records = list(cursor.fetchall())
    article_id = records[0][0]
    author = functional.is_author(article_id, session.get('user'))
    if action == 'delete':
        cursor.execute(f"UPDATE public.article SET isdeleted='{True}' WHERE id={article_id}")
        cursor.execute()
        conn.commit()
        return render_template('draft.html', ban=ban, a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, title=title, text=article_text, author=author, deleted = 1)
    path = f".\\articles\\{article_name}.txt"
    with open(path, "w") as file:
        file.writelines(article_text)
    if action == 'save':
        cursor.execute(f"UPDATE public.article SET title='{title}' WHERE id={article_id}")
        return render_template('draft.html', ban=ban, a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, title=title, text=article_text, author=author, save = 1)
    elif action == 'publish':
        cursor.execute(f"UPDATE public.article_status SET status_id=2 WHERE article_id={article_id}")
        cursor.execute(f"UPDATE public.article SET title='{title}' WHERE id={article_id}")
        conn.commit()
        return render_template('draft.html', ban=ban, a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, title=title, text=article_text, author=author, publish = 1)
    elif action == 'edit':
        return redirect(url_for('.editors', article_name=article_name))


@app.route("/editors/<article_name>", methods=['GET'])
def editors_start(article_name):
    article_id = cursor.execute(f"SELECT * FROM public.article WHERE name='{article_name}'")
    records = list(cursor.fetchall())
    return functional.authorization_editors_check(records[0][0])

@app.route("/editors/<article_name>", methods=['POST'])
def editors(article_name):
    cursor.execute(f"SELECT * FROM public.article WHERE name='{article_name}'")
    records = list(cursor.fetchall())
    article_id = records[0][0]
    username=request.form.get('editor')
    roles = session.get('role')
    ban = session.get('ban')
    new_publish = f"({functional.check_writer_uploads()})"
    role = request.form.get('role')
    cursor.execute(f"SELECT * FROM public.users WHERE login='{username}'")
    records = list(cursor.fetchall())
    if records == []:
        return render_template('editors.html', ban=ban, a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, no_user=1)
    else:
        user_id = records[0][0]
        if role == 'author':
            cursor.execute(f"INSERT INTO public.article_writer(article_id, user_id, isauthor) VALUES ({article_id}, {user_id}, {True})")
            conn.commit()
            return render_template('editors.html', ban=ban, a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, author=1, username=username)
        else:
            cursor.execute(f"INSERT INTO public.article_writer(article_id, user_id, isauthor) VALUES ({article_id}, {user_id}, {False})")
            conn.commit()
            return render_template('editors.html', ban=ban, a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, redactor=1, username=username)


@app.route("/published", methods=['GET'])
def published_start():
    return functional.authorization_check(1, "published")
    
@app.route("/published/<article_name>", methods=['GET'])
def published(article_name):
    return functional.authorization_check_published(article_name)

@app.route("/published/<article_name>", methods=['POST'])
def a_published(article_name):
    action = request.form.get('action')
    cursor.execute(f"SELECT * FROM public.article WHERE name='{article_name}'")
    records = list(cursor.fetchall())
    article_id = records[0][0]
    title = records[0][2]
    roles = session.get('role')
    ban = session.get('ban')
    new_publish = f"({functional.check_writer_uploads()})"
    path = f".\\articles\\{article_name}.txt"
    text = functional.form_text(path)
    if action == "aproove":
        time = functional.get_current_date()
        cursor.execute(f"UPDATE public.article_status SET status_id={3}, date='{time}' WHERE article_id={article_id}")
        conn.commit()
        with open(f".\\reviews\\{article_name}.txt", "w") as file:
            file.write("")
        file.close()
        return render_template('a_published.html', ban=ban, a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, title=title, text=text, aprooved=1)
    else:
        reason = request.form.get('reason')
        cursor.execute(f"UPDATE public.article_status SET status_id={4} WHERE article_id={article_id}")
        cursor.execute(f"UPDATE public.article SET description='{reason}' WHERE id={article_id}")
        conn.commit()
        return render_template('a_published.html', ban=ban, a=roles[0], m=roles[1], w=roles[2], new_publish=new_publish, title=title, text=text, denied=1)

@app.route("/<article_name>", methods=['GET'])
def render_article(article_name):
    return functional.authorization_check_article(article_name)

@app.route("/<article_name>", methods=['POST'])
def save_review(article_name):
    rate = request.form.get('rate')
    review = request.form.get('review')
    user_id = session.get('user')
    action = request.form.get('send')
    path = f".\\reviews\\{article_name}.txt"
    with open(path, "r") as file:
        lines = file.readlines()
    file.close()
    lines += f"{user_id}:{review}\n"
    text = functional.form_article(lines)
    with open(path, "w") as file:
        file.write(text)
    file.close()
    cursor.execute(f"SELECT * FROM public.article WHERE name='{article_name}'")
    records = list(cursor.fetchall())
    article_id = records[0][0]
    time = functional.get_current_date()
    cursor.execute(f"INSERT INTO public.rating (user_id, article_id, date, rate, isdeleted) VALUES ({user_id}, {article_id}, '{time}', {rate}, {False})")
    conn.commit()
    return functional.authorization_check_article(article_name)


@app.route("/archive", methods=['GET'])
def archive_start():
    return functional.authorization_check(3, 'archive')

@app.route("/data/", methods=['GET'])
def get_home_data():
    archive_array = functional.select_table_desc()
    published_array = functional.select_table_published()
    personal_array = functional.select_table_personal()
    home_array = functional.select_table_recent()
    article_id = session.get('article_id')
    if article_id != None:
        reviews_array = functional.select_reviews()
        return {'home': home_array, 'published': published_array, 'personal': personal_array, 'reviews': reviews_array, 'archive': archive_array}
    return {'home': home_array, 'published': published_array, 'personal': personal_array, 'archive': archive_array}
    

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run()