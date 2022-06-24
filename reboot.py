import requests, psycopg2, cv2

#URL = "http://127.0.0.1:5000"

def insert_admin():
    cursor.execute(f"SELECT * FROM public.role_user WHERE role_id=1")
    records = list(cursor.fetchall())
    if records == []:
        username = str(input("Admin's login:"))
        password = str(input("Admin's password:"))
        fullname = str(input("Admin's fullname:"))
        cursor.execute(f"INSERT INTO public.users (id, login, password, fullname, banned) VALUES (1, '{username}', '{password}', '{fullname}', {False})")
        conn.commit()
        print("Administrator is inserted.")
    else:
        print("Administrator already exists.")
    return 0

def insert_roles():
    cursor.execute(f"SELECT * FROM public.role WHERE id=1")
    records = list(cursor.fetchall())
    if records == []:
        cursor.execute(f"INSERT INTO public.role (id, name, description) VALUES (1, 'admin', 'Server administrator')")
        conn.commit()
    cursor.execute(f"SELECT * FROM public.role WHERE id=2")
    records = list(cursor.fetchall())
    if records == []:
        cursor.execute(f"INSERT INTO public.role (id, name, description) VALUES (2, 'moderator', 'Server moderator')")
        conn.commit()
    cursor.execute(f"SELECT * FROM public.role WHERE id=3")
    records = list(cursor.fetchall())
    if records == []:
        cursor.execute(f"INSERT INTO public.role (id, name, description) VALUES (3, 'writer', 'Article writer')")
        conn.commit()
    cursor.execute(f"SELECT * FROM public.role WHERE id=4")
    records = list(cursor.fetchall())
    if records == []:
        cursor.execute(f"INSERT INTO public.role (id, name, description) VALUES (4, 'reader', 'Article reader')")
        conn.commit()
    print("Roles are inserted.")
    return 0
    
def insert_statuses():
    cursor.execute(f"SELECT * FROM public.status WHERE id=1")
    records = list(cursor.fetchall())
    if records == []:
        cursor.execute(f"INSERT INTO public.status (id, name, description) VALUES (1, 'draft', 'Article has draft status')")
        conn.commit()
    cursor.execute(f"SELECT * FROM public.status WHERE id=2")
    records = list(cursor.fetchall())
    if records == []:
        cursor.execute(f"INSERT INTO public.status (id, name, description) VALUES (2, 'published', 'Article sent to moderator')")
        conn.commit()
    cursor.execute(f"SELECT * FROM public.status WHERE id=3")
    records = list(cursor.fetchall())
    if records == []:
        cursor.execute(f"INSERT INTO public.status (id, name, description) VALUES (3, 'aprooved', 'Moderator aprooved article')")
        conn.commit()
    cursor.execute(f"SELECT * FROM public.status WHERE id=4")
    records = list(cursor.fetchall())
    if records == []:
        cursor.execute(f"INSERT INTO public.status (id, name, description) VALUES (4, 'denied', 'Moderator denied article')")
        conn.commit()
    print("Statuses are inserted.")
    return 0

def insert_topics():
    cursor.execute(f"SELECT * FROM public.topic WHERE id=1")
    records = list(cursor.fetchall())
    if records == []:
        cursor.execute(f"INSERT INTO public.topic (id, name) VALUES (1, 'science')")
        conn.commit()
    cursor.execute(f"SELECT * FROM public.topic WHERE id=2")
    records = list(cursor.fetchall())
    if records == []:
        cursor.execute(f"INSERT INTO public.topic (id, name) VALUES (2, 'art')")
        conn.commit()
    cursor.execute(f"SELECT * FROM public.topic WHERE id=3")
    records = list(cursor.fetchall())
    if records == []:
        cursor.execute(f"INSERT INTO public.topic (id, name) VALUES (3, 'history')")
        conn.commit()
    cursor.execute(f"SELECT * FROM public.topic WHERE id=4")
    records = list(cursor.fetchall())
    if records == []:
        cursor.execute(f"INSERT INTO public.topic (id, name) VALUES (4, 'news')")
        conn.commit()
    print("Topics are inserted.")
    return 0

if __name__ == '__main__':
    conn = psycopg2.connect(database="server_db",
                                user="postgres",
                                password="postgres",
                                host="localhost",
                                port="5432")
    cursor = conn.cursor()
    insert_roles()
    insert_statuses()
    insert_topics()
    insert_admin()
    

 