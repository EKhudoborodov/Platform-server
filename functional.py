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
            return flask.render_template("editors.html", a = user_roles[0], m = user_roles[1], w = user_roles[2], ban = ban, new_publish=new_publish)
        else:
            return flask.redirect(flask.url_for('.home'))

def authorization_check_published(article_name):
    ban = flask.session.get('ban')
    user_roles = flask.session.get('role')
    if user_roles == None:
        return flask.redirect(flask.url_for('.sign_in_start'))
    elif user_roles[0] == 1 or user_roles[1] == 1:
        #a - admin, m - moder, w - writer, r - reader;
        new_publish = f"({check_writer_uploads()})"
        cursor.execute(f"SELECT * FROM public.article WHERE name='{article_name}' and isdeleted = {False}")
        records = list(cursor.fetchall())
        if records == []:
            return flask.render_template("a_published.html", a = user_roles[0], m = user_roles[1], w = user_roles[2], ban = ban, new_publish=new_publish, no_article=1)
        else:
            article_id = records[0][0]
            title = records[0][2]
            cursor.execute(f"SELECT * FROM public.article_status WHERE article_id={article_id}")
            check = list(cursor.fetchall())
            path = f".\\articles\\{article_name}.txt"
            text = form_text(path)
            if check[0][1] == 2:
                return flask.render_template("a_published.html", a = user_roles[0], m = user_roles[1], w = user_roles[2], ban = ban, new_publish=new_publish, text=text, title=title)
            elif check[0][1] == 3:    
                return flask.render_template("a_published.html", a = user_roles[0], m = user_roles[1], w = user_roles[2], ban = ban, new_publish=new_publish, text=text, title=title, aprooved=1)
            elif check[0][1] == 4:
                return flask.render_template("a_published.html", a = user_roles[0], m = user_roles[1], w = user_roles[2], ban = ban, new_publish=new_publish, text=text, title=title, denied=1)    
    else:
        return flask.redirect(flask.url_for('.home'))

def authorization_check_article(article_name):
    ban = flask.session.get('ban')
    user_roles = flask.session.get('role')
    if user_roles == None:
        return flask.redirect(flask.url_for('.sign_in_start'))
    else:
        new_publish = f"({check_writer_uploads()})"
        cursor.execute(f"SELECT * FROM public.article WHERE name='{article_name}' and isdeleted = {False}")
        records = list(cursor.fetchall())
        if records == []:
            return flask.render_template("article.html", a = user_roles[0], m = user_roles[1], w = user_roles[2], ban = ban, new_publish=new_publish, no_article=1)
        else:
            article_id = records[0][0]
            title = records[0][2]
            #path = f".\\reviews\\{article_name}.txt"
            #reviews = form_text(path)
            path = f".\\articles\\{article_name}.txt"
            text = form_text(path)
        return flask.render_template(f"article.html", a = user_roles[0], m = user_roles[1], w = user_roles[2], ban = ban, new_publish=new_publish, text=text, )

def check_writer_uploads():
    cursor.execute(f"SELECT * FROM public.article_status WHERE status_id=2")
    records = list(cursor.fetchall())
    res = 0
    for i in records:
        res+=1
    return res

def form_text(path):
    check = 1
    with open(path, "r") as text_file:
        lines = text_file.readlines()
    text_file.close()
    if path[2:10] == 'articles':
        return form_article(lines)
    #else:
        #return form_reviews(lines)

def form_article(lines):
    if lines == []:
        return None
    else:
        new_lines = ""
        for line in lines:
            if line != "\n" or check == 1:
                new_lines += line
                check = 0
            else:
                check = 1
        #print(new_lines)
        return new_lines


"""
def form_reviews(article_id):
    res = ""
    cursor.execute(f"SELECT * FROM public.rating WHERE article_id={article_id} and isdeleted={False}")
    rating = list(cursor.fetchall())
    if rating == []:
        return None
    else:
        for i in (len(rating)-1, 0, -1):
            cursor.execute(f"SELECT * FROM public.users WHERE id={rating[i][1]} and isbanned={False}")
            records = list(cursor.fetchall())
            username = records[0][1]
            fullname = records[0][3]
"""     
     


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
        return flask.render_template('workshop.html', a = roles[0], m = roles[1], w = roles[2], new_publish=new_publish)
    else:
        first, second, third = None, None, None
        for i in range (len(records)-1, -1, -1):
            article_id = records[i][0]
            cursor.execute(f"SELECT * FROM public.article WHERE id={article_id}")
            recs = list(cursor.fetchall())
            if recs != []:
                if i == len(records)-1:
                    first = recs[0][1]
                elif i == len(records)-2:
                    second = recs[0][1]
                elif i == len(records)-3:
                    third = recs[0][1]
                else: 
                    break
            else:
                break
        return flask.render_template('workshop.html', ban=ban, a=roles[0], m=roles[1], w=roles[2], first=first, second=second, third=third, new_publish=new_publish, no_article=no_article)

"""
def build_html(direction):
    path = f".\\templates\\{direction}.html"
    with open(path, "r") as text_file:
        lines = text_file.readlines()
    text_file.close()
    rem = 0
    res = ""
    for i in range (len(lines)):
        if rem == 0:
            res += lines[i]
        if lines[i] == "\t\t\t\tvar myArray = [\n":
            rem = 1
        elif lines[i] == "\t\t\t\t]\n":
            if direction == 'home':
                res += select_table_desc() + lines[i]
            else:
                res += select_table_published() + lines[i]
            rem = 0
    with open(path, "w") as file:
        file.write(res)
    file.close()
    return 0
"""

def select_table_desc():
    cursor.execute(f"SELECT * FROM public.article WHERE isdeleted={False}")
    records = list(cursor.fetchall())
    array = []
    for rec in records:
        article_id = rec[0]
        name = rec[1]
        cursor.execute(f"SELECT * FROM public.article_status WHERE article_id={article_id}")
        check = list(cursor.fetchall())
        if check[0][1] == 3:
            cursor.execute(f"SELECT * FROM public.article_writer WHERE article_id={article_id}")
            article_desc = list(cursor.fetchall())
            authors = ""
            for log in article_desc:
                cursor.execute(f"SELECT * FROM public.users WHERE id={log[1]}")
                desc = list(cursor.fetchall())
                authors += desc[0][3] + ", "
            authors=authors[0:len(authors)-2]
            cursor.execute(f"SELECT * FROM public.article_topic WHERE article_id={article_id}")
            article_desc = list(cursor.fetchall())
            cursor.execute(f"SELECT * FROM public.topic WHERE id={article_desc[0][1]}")
            topic_desc = list(cursor.fetchall())
            topic = topic_desc[0][1]
            cursor.execute(f"SELECT * FROM public.rating WHERE article_id={article_id} and isdeleted={False}")
            rating_desc = list(cursor.fetchall())
            count = 0
            for log in rating_desc:
                count += log[4]
            if count!=0:
                reviews = count/len(rating_desc)
            else:
                reviews='-'
            array += {'name':name, 'author': authors, 'topic': topic, 'reviews': reviews},
    return array

def select_table_published():
    cursor.execute(f"SELECT * FROM public.article_status WHERE status_id={2}")
    records = list(cursor.fetchall())
    array = []
    for rec in records:
        article_id = rec[0]
        cursor.execute(f"SELECT * FROM public.article WHERE id={article_id}")
        article_desc = list(cursor.fetchall())
        name = article_desc[0][1]
        cursor.execute(f"SELECT * FROM public.article_writer WHERE article_id={article_id}")
        check = list(cursor.fetchall())
        authors = ""
        for log in check:
            cursor.execute(f"SELECT * FROM public.users WHERE id={log[1]}")
            desc = list(cursor.fetchall())
            authors += desc[0][3] + ", "
        authors=authors[0:len(authors)-2]
        cursor.execute(f"SELECT * FROM public.article_topic WHERE article_id={article_id}")
        article_desc = list(cursor.fetchall())
        cursor.execute(f"SELECT * FROM public.topic WHERE id={article_desc[0][1]}")
        topic_desc = list(cursor.fetchall())
        topic = topic_desc[0][1]
        reviews = '-'
        array += {'name': name, 'author': authors, 'topic': topic, 'reviews': reviews},
    return array

def select_table_personal():
    user_id = flask.session.get('user')
    cursor.execute(f"SELECT * FROM public.article_writer WHERE user_id={user_id}")
    records = list(cursor.fetchall())
    array = []
    for rec in records:
        article_id = rec[0]
        cursor.execute(f"SELECT * FROM public.article WHERE id={article_id}")
        article_desc = list(cursor.fetchall())
        name = article_desc[0][1]
        cursor.execute(f"SELECT * FROM public.article_writer WHERE article_id={article_id}")
        check = list(cursor.fetchall())
        authors = ""
        for log in check:
            cursor.execute(f"SELECT * FROM public.users WHERE id={log[1]}")
            desc = list(cursor.fetchall())
            authors += desc[0][3] + ", "
        authors=authors[0:len(authors)-2]
        cursor.execute(f"SELECT * FROM public.article_topic WHERE article_id={article_id}")
        article_desc = list(cursor.fetchall())
        cursor.execute(f"SELECT * FROM public.topic WHERE id={article_desc[0][1]}")
        topic_desc = list(cursor.fetchall())
        topic = topic_desc[0][1]
        cursor.execute(f"SELECT * FROM public.rating WHERE article_id={article_id} and isdeleted={False}")
        rating_desc = list(cursor.fetchall())
        count = 0
        for log in rating_desc:
            count += log[4]
        if count!=0:
            reviews = count/len(rating_desc)
        else:
            reviews='-'
        array += {'name': name, 'author': authors, 'topic': topic, 'reviews': reviews},
    return array


if __name__ == '__main__':
    with open(".\\reviews\\test2.txt", "w") as file:
        file.write("")
    file.close()
    with open(".\\reviews\\test3.txt", "w") as file:
        file.write("")
    file.close()
    with open(".\\reviews\\denis.txt", "w") as file:
        file.write("")
    file.close()



"""  
if __name__ == '__main__':
    array = select_table_desc()
    print(array)
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
    path = f".\\articles\\test3.txt"
    with open(path, "r") as text_file:
        lines = text_file.readlines()
    text_file.close()
    print(lines)
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
    
    

 