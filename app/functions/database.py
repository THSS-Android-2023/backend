import datetime

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
        status, res = db_get_followings(username_1)
        if not status:
            return False, res
        if username_2 in [user['username'] for user in res]:
            return False, "the target user has been followed"
        followship = Followship(username_1=username_1, username_2=username_2)
        db.session.add(followship)
        db.session.commit()
        return True, "success"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_unfollow_user(username_1, username_2):
    try:
        status, res = db_get_followings(username_1)
        if not status:
            return False, res
        if username_2 not in [user['username'] for user in res]:
            return False, "the target user has not been followed"
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
        status, res = db_get_user_blacklist(username_1)
        if not status:
            return False, res
        if username_2 in res:
            return False, "the target user has been blocked"
        blackship = Blackship(username_1=username_1, username_2=username_2)
        db.session.add(blackship)
        db.session.commit()
        return True, "success"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_unblack_user(username_1, username_2):
    try:
        status, res = db_get_user_blacklist(username_1)
        if not status:
            return False, res
        if username_2 in res:
            return False, "the target user has not been blocked"
        db.session.execute(f"DELETE FROM followship WHERE username_1 = '{username_1}' AND username_2 ='{username_2}';")
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
    

def db_add_new_moment(username, title, content, img_nums, tag):
    try:
        create_time = datetime.datetime.now()
        moment = Moment(username=username, title=title, content=content, img_nums=img_nums, time=create_time, tag=tag)
        db.session.add(moment)
        db.session.commit()
        cursor = db.session.execute(f"SELECT id FROM moment WHERE username = '{username}' AND time = '{create_time}';")
        for cur in cursor:
            return True, cur[0]
        return False, "can not find id of the moment"
    except Exception as e:
        print(str(e))
        return False, str(e)


# 按用户名获取动态
def db_get_user_moment(current_user, target_user, page):
    """
    parameters:
        page: 按每10条动态开始分页，page从0开始索引，默认从新到旧返回。例如page==1则返回从新到旧的第11-20条动态
    """
    try:
        cursor = db.session.execute(f"SELECT id, username, title, content, img_nums, tag, time FROM moment WHERE username = '{target_user}' ORDER BY id DESC LIMIT 10 OFFSET {page * 10};")
        moments = []
        for cur in cursor:
            moment = {'id': cur[0], 'username': cur[1], 'title': cur[2], 'content': cur[3], 'img_nums': cur[4], 'tag': cur[5], 'time': cur[6]}
            cursor_star = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{cur[0]}' AND _type = 'False'")
            star_user_list = [row[0] for row in cursor_star.fetchall()]
            moment['is_current_user_star'] = current_user in star_user_list
            moment['star_nums'] = len(star_user_list)

            cursor_like = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{cur[0]}' AND _type = 'True'")
            like_user_list = [row[0] for row in cursor_like.fetchall()]
            moment['is_current_user_like'] = current_user in like_user_list
            moment['like_nums'] = len(like_user_list)
            moments.append(moment)
        return True, moments
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_user_star_moment_id_list(username):
    try:
        cursor = db.session.execute(f"SELECT moment_id FROM like_and_star WHERE username = '{username}' AND _type = 'False'")
        star_moment_id_list = [cur[0] for cur in cursor]
        return True, star_moment_id_list
    except Exception as e:
        print(str(e))
        return False, str(e)
    

def db_get_moment_by_id(username, moment_id):
    try:
        cursor = db.session.execute(f"SELECT id, username, title, content, img_nums, tag, time FROM moment WHERE id = '{moment_id}';")
        moment = {}
        for cur in cursor:
            moment = {'id': cur[0], 'username': cur[1], 'title': cur[2], 'content': cur[3], 'img_nums': cur[4], 'tag': cur[5], 'time': cur[6]}
            cursor_star = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{cur[0]}' AND _type = 'False'")
            star_user_list = [row[0] for row in cursor_star.fetchall()]
            moment['is_current_user_star'] = username in star_user_list
            moment['star_nums'] = len(star_user_list)

            cursor_like = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{cur[0]}' AND _type = 'True'")
            like_user_list = [row[0] for row in cursor_like.fetchall()]
            moment['is_current_user_like'] = username in like_user_list
            moment['like_nums'] = len(like_user_list)
        return True, moment
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_star_moment(username, moment_id):
    try:
        status, res = db_get_user_star_moment_id_list(username)
        if not status:
            return False, res
        if moment_id in res:
            return False, "the moment has been stared by the user"
        like_and_star = LikeAndStar(moment_id=moment_id, _type=False, username=username)
        db.session.add(like_and_star)
        db.session.commit()
        return True, "success"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_unstar_moment(username, moment_id):
    try:
        status, res = db_get_user_star_moment_id_list(username)
        if not status:
            return False, res
        if moment_id not in res:
            return False, "the moment has not been stared by the user"
        db.session.execute(f"DELETE FROM like_and_star WHERE moment_id = '{moment_id}' AND username ='{username}' AND _type = 'False';")
        db.session.commit()
        return True, "success"
    except Exception as e:
        print(str(e))
        return False, str(e)
    