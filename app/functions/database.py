from app.models.models import Users, Followship
from app.extensions.extensions import db


# 添加新的用户
def db_add_new_user(username, password):
    try:
        user = Users(username=username, password=password, intro='', avatar='http://129.211.216.10:5001/static/default.png', nickname=username)
        db.session.add(user)
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False


# 修改用户信息
def db_change_user_info(username, intro, nickname):
    try:
        status, res = db_get_user_info(username)
        if not status:
            return False
        if intro is None:
            intro = res['intro']
        if nickname is None:
            nickname = res['nickname']
        db.session.execute("UPDATE users SET intro = '{}', nickname = '{}' WHERE username = '{}';".format(intro, username, nickname))
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False


# 修改密码
def db_change_user_password(username, new_password):
    try:
        db.session.execute("UPDATE users SET password = '{}' WHERE username = '{}';".format(new_password, username))
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False


# 用户认证
def db_verify_user(username, password):
    try:
        cursor = db.session.execute("SELECT password FROM users WHERE username ='{}';".format(username))
        for cur in cursor:
            pw = cur[0]
        return password == pw
    except Exception as e:
        print(e)
        return False


def db_get_user_info(username):
    try:
        cursor = db.session.execute("SELECT intro, avatar, nickname FROM users WHERE username = '{}';".format(username))
        for cur in cursor:
            return True, {'intro': cur[0], 'avatar': cur[1], 'nickname': cur[2]}
        return False, "no such user"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_follow_user(username_1, username_2):
    try:
        followship = Followship(username_1=username_1, username_2=username_2)
        db.session.add(followship)
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_unfollow_user(username_1, username_2):
    try:
        db.session.execute("DELETE FROM followship WHERE username_1 = '{}' and username_2 ='{}';".format(username_1, username_2))
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False, str(e)
