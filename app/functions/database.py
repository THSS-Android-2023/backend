from app.models.models import *
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
        db.session.execute(f"UPDATE users SET intro = '{intro}', nickname = '{nickname}' WHERE username = '{username}';")
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False


def db_change_user_avatar(username, avatar):
    try:
        db.session.execute(f"UPDATE users SET avatar = '{avatar}' WHERE username = '{username}';")
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False


# 修改密码
def db_change_user_password(username, new_password):
    try:
        db.session.execute(f"UPDATE users SET password = '{new_password}' WHERE username = '{username}';")
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False


# 用户认证
def db_verify_user(username, password):
    try:
        cursor = db.session.execute(f"SELECT password FROM users WHERE username ='{username}';")
        for cur in cursor:
            pw = cur[0]
        return password == pw
    except Exception as e:
        print(e)
        return False


def db_get_user_info(username):
    try:
        status, res = db_get_followings(username)
        if not status:
            return False, "get followings error"
        followings_num = len(res)
        status, res = db_get_followers(username)
        if not status:
            return False, "get followers error"
        followers_num = len(res)
        cursor = db.session.execute(f"SELECT intro, avatar, nickname FROM users WHERE username = '{username}';")
        for cur in cursor:
            return True, {'intro': cur[0], 'avatar': cur[1], 'nickname': cur[2], 'followers_num': followers_num, "followings_num": followings_num}
        return False, "no such user"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_follow_user(username_1, username_2):
    try:
        followship = Followship(username_1=username_1, username_2=username_2)
        db.session.add(followship)
        db.session.commit()
        return True, "success"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_unfollow_user(username_1, username_2):
    try:
        db.session.execute(f"DELETE FROM followship WHERE username_1 = '{username_1}' and username_2 ='{username_2}';")
        db.session.commit()
        return True, "success"
    except Exception as e:
        print(str(e))
        return False, str(e)

# 获取粉丝列表
def db_get_followers(username):
    try:
        cursor = db.session.execute(
            f"""SELECT users.username, users.intro, users.avatar, users.nickname 
                FROM followship
                JOIN users ON followship.username_2 = users.username
                where followship.username_1 = '{username}'
                ;""")
        results = cursor.fetchall()
        followers_list = []
        followings_list = db_get_followings(username)
        for result in results:
            followers_list.append({
                'username': result[0],
                'intro': result[1],
                'avatar': result[2],
                'nickname': result[3],
                "is_following": result[0] in followings_list
            })
        return True, followers_list
    except Exception as e:
        print(str(e))
        return False, str(e)
    

# 获取关注用户列表
def db_get_followings(username):
    try:
        cursor = db.session.execute(
            f"""SELECT users.username, users.intro, users.avatar, users.nickname 
                FROM followship
                JOIN users ON followship.username_1 = users.username
                where followship.username_2 = '{username}'
                ;""")
        results = cursor.fetchall()
        followings_list = []
        for result in results:
            followings_list.append({
                'username': result[0],
                'intro': result[1],
                'avatar': result[2],
                'nickname': result[3]
            })
        return True, followings_list
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_black_user(username_1, username_2):
    try:
        followship = Blackship(username_1=username_1, username_2=username_2)
        db.session.add(followship)
        db.session.commit()
        return True, "success"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_unblack_user(username_1, username_2):
    try:
        db.session.execute(f"DELETE FROM followship WHERE username_1 = '{username_1}' and username_2 ='{username_2}';")
        db.session.commit()
        return True, "success"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_user_blacklist(username):
    try:
        cursor = db.session.execute(f"SELECT username_2 FROM blackship WHERE username_1 = '{username}';")
        blacklist = []
        for cur in cursor:
            blacklist.append(cur[0])
        return True, blacklist
    except Exception as e:
        print(str(e))
        return False, str(e)
    

