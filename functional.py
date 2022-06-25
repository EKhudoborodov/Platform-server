import requests, psycopg2, cv2
import flask

def stop_sessions():
    flask.session['user'] = None
    flask.session['fullname'] = None
    flask.session['role'] = None
    flask.session['ban'] = None
    flask.session['article'] = None
    flask.session['article_id'] = None
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

def authorization_check(user_roles, validate_role, direction):
    if user_roles == None:
        return flask.redirect(flask.url_for('.sign_in_start'))
    elif user_roles[0] == 1 or user_roles[validate_role] == 1:
        return flask.render_template(f"{direction}.html")
    else:
        return flask.redirect(flask.url_for('.home'))
        
    

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
"""
    
    

 