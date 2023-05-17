from flask import Blueprint, Flask, request, session, jsonify
import sqlite3 as sql
from werkzeug.security import generate_password_hash, check_password_hash
import time
import json

database_bp = Blueprint("database", __name__)
DB_DIR = 'database.db'


database_bp = Blueprint("database", __name__)


# use blueprint as app
@database_bp.route("/")
def database_index():
    return "Database Index"

@database_bp.route("/init/", methods=['POST'])
def db_init():
    conn = sql.connect(DB_DIR)
    conn.execute("PRAGMA foreign_keys=ON;")
    print("Created / Opened database successfully")
    try:
         conn.execute("SELECT * FROM " + 'users;') 
         print("Table opened successfully")
    except:
        conn.execute('''
            CREATE TABLE users
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                pwhash TEXT NOT NULL,
                intro TEXT,
                avatar TEXT,
                star_user TEXT
            );''')
        print("Table created successfully")
    conn.close()
    return None

# insert a user
def db_insertuser(name, pw):
    pwhash= generate_password_hash('NAME:'+name+'|PW:'+pw,method='pbkdf2:sha256',salt_length=8)
    try:
        conn = sql.connect(DB_DIR)

        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute("INSERT INTO users (username, pwhash, intro, avatar, star_user) \
            VALUES ('"+name+"','"+pwhash+"','','','');")
        conn.commit()
        conn.close()
        return True

    except sql.Error as error:
        print("Failed to insert data into sqlite table", error)
        if conn:
            conn.close()
        return False

# verify a user's name and password, True for successful, False for failed
def db_verify_pw(name, pw):
    try:
        pw = 'NAME:'+name+'|PW:'+pw
        pwhash = db_selectUserByName(name)[1]
        # print("verify",db_selectUserByName(name)[1])
        return check_password_hash(pwhash, pw)
    except:
        return False

# delete a user, True for successful, False for failed
def db_deleteuser(name, pw):
    try:
        if db_verify_pw(name, pw):
            container_list = db_selectContainerByUser(name)
            conn = sql.connect(DB_DIR)
            conn.execute("PRAGMA foreign_keys=ON;")
            if container_list:
                for i in container_list:
                    docker_rm(i[1])
            conn.execute("DELETE FROM users WHERE username ='"+name+"';") # delete cascade
            conn.commit()
            print("Total number of rows deleted :%d"%conn.total_changes)
            conn.close()
            return True
        else:
            print("Failed to delete data from sqlite table", "name/pw wrong!")
            return False
    except sql.Error as error:
        print("Failed to delete data from sqlite table", error)
        if conn:
            conn.close()
        return False

# select user by name, return tuple: (userid, pwhash)
def db_selectUserByName(name):
    try:
        conn = sql.connect(DB_DIR)
        conn.execute("PRAGMA foreign_keys=ON;")
        cur = conn.execute("SELECT id, pwhash FROM users WHERE username ='"+name+"';")
        res = None
        for i in cur:
            res = (i[0], i[1])
        conn.commit()
        conn.close()
        return res
    except sql.Error as error:
        print("Failed to select data from sqlite table", error)
        if conn:
            conn.close()
        return None


def db_change_user_info(username, intro, avatar):
    try:
        conn = sql.connect(DB_DIR)
        conn.execute("PRAGMA foreign_keys=ON;")
        cur = conn.execute("UPDATE users SET intro = '" + str(intro) + "' WHERE username = '" + str(username) + "';")
        cur = conn.execute("UPDATE users SET avatar = '" + str(avatar) + "' WHERE username = '" + str(username) + "';")
        conn.commit()
        conn.close()
        return True, ""
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_user_info(username):
    try:
        conn = sql.connect(DB_DIR)
        conn.execute("PRAGMA foreign_keys=ON;")
        cur = conn.execute("SELECT intro, avatar, star_user FROM users WHERE username ='"+username+"';")
        res = None
        for i in cur:
            star_user = i[2].split(' ')
            res = (i[0], i[1], star_user)
        conn.commit()
        conn.close()
        return True, res
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_change_password(username, old_password, new_password):
    try:
        if not db_verify_pw(username, old_password):
            return False, "verify failed"
        conn = sql.connect(DB_DIR)
        conn.execute("PRAGMA foreign_keys=ON;")
        pwhash= generate_password_hash('NAME:'+username+'|PW:'+new_password,method='pbkdf2:sha256',salt_length=8)
        cur = conn.execute("UPDATE users SET pwhash = '" + str(pwhash) + "' WHERE username = '" + str(username) + "';")
        conn.commit()
        conn.close()
        return True, ""
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_star_user(username, target_user):
    try:
        conn = sql.connect(DB_DIR)
        conn.execute("PRAGMA foreign_keys=ON;")
        cur = conn.execute("SELECT star_user FROM users WHERE username ='"+username+"';")
        star_user = ""
        for i in cur:
            star_user = i[0]
        star_user = star_user + " " + str(target_user)
        cur = conn.execute("UPDATE users SET star_user = '" + str(star_user) + "' WHERE username = '" + str(username) + "';")
        conn.commit()
        conn.close()
        return True, ""
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_unstar_user(username, target_user):
    try:
        conn = sql.connect(DB_DIR)
        conn.execute("PRAGMA foreign_keys=ON;")
        cur = conn.execute("SELECT star_user FROM users WHERE username ='"+username+"';")
        star_user = ""
        for i in cur:
            star_user_list = i[0].split(' ')
        if target_user not in star_user_list:
            return False, 'no such user'
        star_user_list.remove(target_user)
        new_star_user = ""
        for i in star_user_list:
            new_star_user = new_star_user + i
        cur = conn.execute("UPDATE users SET star_user = '" + str(star_user) + "' WHERE username = '" + str(username) + "';")
        conn.commit()
        conn.close()
        return True, ""
    except Exception as e:
        print(str(e))
        return False, str(e)
