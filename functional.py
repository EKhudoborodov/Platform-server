import requests, psycopg2, cv2
import flask

conn = psycopg2.connect(database="server_db",
                        user="postgres",
                        password="postgres",
                        host="localhost",
                        port="5432")

cursor = conn.cursor()

def stop_sessions():
    flask.session['user'] = None
    flask.session['fullname'] = None
    flask.session['role'] = None
    flask.session['ban'] = None
    flask.session['article'] = None
    flask.session['article_id'] = None
    flask.session['title'] = None
    return 0

def crypt_role(role):
    if role=='writer':
        role_id = 3
    elif role=='moderator':
        role_id = 2
    else:
        role_id = 5
    return role_id
    
def send_roles(records):
    roles = []
    for pair in records:
        roles.append(pair[1])
    return roles

def select_role(roles):
    res = [0, 0, 0, 0]
    for role in roles:
        if role == 1:
            res[0]=1
        elif role == 2:
            res[1]=1
        elif role == 3:
            res[2]=1
        elif role == 4:
            res[3]=1
    return res

def authorization_check(validate_role, direction):
    ban = flask.session.get('ban')
    user_roles = flask.session.get('role')
    if user_roles == None:
        return flask.redirect(flask.url_for('.sign_in_start'))
    elif user_roles[0] == 1 or user_roles[validate_role] == 1 or direction == 'home':
        #a - admin, m - moder, w - writer, r - reader;
        new_publish = f"({check_writer_uploads()})"
        return flask.render_template(f"{direction}.html", a = user_roles[0], m = user_roles[1], w = user_roles[2], ban = ban, new_publish=new_publish)
    else:
        return flask.redirect(flask.url_for('.home'))

def authorization_editors_check(article_id):
    ban = flask.session.get('ban')
    user_roles = flask.session.get('role')
    if user_roles == None:
        return flask.redirect(flask.url_for('.sign_in_start'))
    else:
        user = flask.session.get('user')
        cursor.execute(f"SELECT * FROM public.article_writer WHERE user_id={user} and article_id={article_id}")
        records = list(cursor.fetchall())
        if user_roles[0] == 1 or (user_roles[1] == 1 and records[0][2] == True):
            #a - admin, m - moder, w - writer, r - reader;
            new_publish = f"({check_writer_uploads()})"
            return flask.render_template(f"editors.html", a = user_roles[0], m = user_roles[1], w = user_roles[2], ban = ban, new_publish=new_publish)
        else:
            return flask.redirect(flask.url_for('.home'))
        
def check_writer_uploads():
    cursor.execute(f"SELECT * FROM public.article_status WHERE status_id=2")
    records = list(cursor.fetchall())
    res = 0
    for i in records:
        res+=1
    return res

def form_text(path):
    with open(path, "r") as text_file:
        lines = text_file.readlines()
    text_file.close()
    if lines == []:
        return None
    else:
        new_lines = ""
        for line in lines:
            if line != "\n":
                new_lines += line
        #print(new_lines)
        return new_lines

def is_author(article_id, user_id):
    cursor.execute(f"SELECT * FROM public.article_writer WHERE article_id='{article_id}' and user_id='{user_id}'")
    records = list(cursor.fetchall())
    if records[0][2] == True:
        return 1
    else:
        return 0

def workshop_check(user_id, roles, no_article):
    new_publish = f"({check_writer_uploads()})"
    ban = flask.session.get('ban')
    cursor.execute(f"SELECT * FROM public.article_writer WHERE user_id={user_id}")
    records = list(cursor.fetchall())
    if records == []:
        return render_template('workshop.html', a = roles[0], m = roles[1], w = roles[2], new_publish=new_publish)
    else:
        first, second, third = None, None, None
        for i in range (len(records)-1, -1, -1):
            article_id = records[i][0]
            cursor.execute(f"SELECT * FROM public.article WHERE id={article_id}")
            recs = list(cursor.fetchall())
            if i == len(records)-1:
                first = recs[0][1]
            elif i == len(records)-2:
                second = recs[0][1]
            elif i == len(records)-3:
                third = recs[0][1]
            else:
                break
        return flask.render_template('workshop.html', ban=ban, a=roles[0], m=roles[1], w=roles[2], first=first, second=second, third=third, new_publish=new_publish, no_article=no_article)

"""  
if __name__ == '__main__':
    conn = psycopg2.connect(database="server_db",
                                user="postgres",
                                password="postgres",
                                host="localhost",
                                port="5432")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM role_user WHERE user_id=4")
    records = list(cursor.fetchall())
    for i in range(len(records)):
        print(records[i], i)

if __name__ == '__main__':
    path = f".\\articles\\test1.txt"
    form_text(path)
    path = f".\\articles\\copy.txt"
    with open(path, "w") as file:
        file.write("Your text goes here. And reads like this.")
    text_file = open(path, "r")
    lines = text_file.readlines()
    print(lines[0])
    with open("copy.txt", "w") as file:
        file.write("Your text goes here")
    conn = psycopg2.connect(database="server_db",
                                user="postgres",
                                password="postgres",
                                host="localhost",
                                port="5432")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM role_user WHERE user_id=4")
    records = list(cursor.fetchall())
"""
    
    

 