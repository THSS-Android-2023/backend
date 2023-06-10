import datetime

from sqlalchemy import func, or_, and_

from app.models.models import *
from app.extensions.extensions import db
from dateutil import parser


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


def db_check_followship(username1, username2):
    try:
        cursor = db.session.execute(f"SELECT * FROM followship WHERE username_1 = '{username1}' AND username_2 = '{username2}';")
        for cur in cursor:
            return True, True
        return True, False
    except Exception as e:
        print(e)
        return False, False


def db_get_user_info(username):
    try:
        status, res = db_get_followings(username)
        if not status:
            return False, "get followings error"
        print("followings", res)
        followings_num = len(res)
        status, res = db_get_followers(username)
        if not status:
            return False, "get followers error"
        print("followers", res)
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
        print(username_1, username_2)
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
                JOIN users ON followship.username_1 = users.username
                where followship.username_2 = '{username}'
                ;""")
        results = cursor.fetchall()
        followers_list = []
        followings_list = db_get_followings(username)[1]
        followings_list = [user['username'] for user in followings_list]
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
                JOIN users ON followship.username_2 = users.username
                where followship.username_1 = '{username}'
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
        if username_2 not in res:
            return False, "the target user has not been blocked"
        db.session.execute(f"DELETE FROM blackship WHERE username_1 = '{username_1}' AND username_2 ='{username_2}';")
        db.session.commit()
        return True, "success"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_nickname(username):
    for cur in db.session.execute(f"SELECT nickname FROM users WHERE username = '{username}';"):
        return True, cur[0]
    return False, "no such user"


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
    

def db_add_new_moment(username, title, content, img_nums, tag, location, _type):
    try:
        create_time = datetime.datetime.now()
        moment = Moment(username=username, title=title, content=content, img_nums=img_nums, time=create_time, tag=tag, location=location, _type=_type)
        db.session.add(moment)
        db.session.commit()
        cursor = db.session.execute(f"SELECT id FROM moment WHERE username = '{username}' AND time = '{create_time}';")
        for cur in cursor:
            status, res = db_get_followers(username)
            if not status:
                return False, res
            for follower in res:
                if not db_add_notice(username, follower['username'], cur[0], '3'):
                    return False, 'add notice failed'
            return True, cur[0]
        return False, "can not find id of the moment"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_del_moment(username, moment_id):
    try:
        cursor = db.session.execute(f"SELECT username FROM moment WHERE id = '{moment_id}';")
        for cur in cursor:
            if username == cur[0]:
                db.session.execute(f"DELETE FROM moment WHERE id = '{moment_id}';")
                db.session.commit()
                return True, ''
            return False, 'user error'
        return False, 'no such moment'
    except Exception as e:
        print(str(e))
        return False, str(e)


# 按用户名获取动态
def db_get_user_moment(current_user, target_user, base_id):
    try:
        status, followings_list = db_get_followings(current_user)
        followings_list = [user['username'] for user in followings_list]
        if base_id != '':
            cursor = db.session.execute(f"SELECT id, username, title, content, img_nums, tag, location, _type, time FROM moment WHERE username = '{target_user}' AND id < {base_id} ORDER BY id DESC LIMIT 10;")
        else:
            cursor = db.session.execute(f"SELECT id, username, title, content, img_nums, tag, location, _type, time FROM moment WHERE username = '{target_user}' ORDER BY id DESC LIMIT 10;")
        moments = []
        status, res = db_get_nickname(target_user)
        if not status:
            return False, res
        for cur in cursor:
            if str(cur[7]) == '0':
                mp4url = ''
            else:
                mp4url = 'http://129.211.216.10:5001/static/moment_imgs/' + str(cur[0]) + '_1.mp4'
            moment = {'id': cur[0], 'username': cur[1], 'nickname': res, 'title': cur[2], 'content': cur[3], 'img_nums': cur[4], 'tag': cur[5], 'location':cur[6], 'mp4url': mp4url, 'time': format_time(cur[8])}
            cursor_star = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{cur[0]}' AND _type = False;")
            star_user_list = [row[0] for row in cursor_star.fetchall()]
            moment['is_current_user_star'] = current_user in star_user_list
            moment['star_nums'] = len(star_user_list)

            moment['is_current_user_following'] = cur[1] in followings_list
            
            moment['avatar'] = db.session.execute(f"SELECT avatar FROM users WHERE username = '{moment['username']}';").fetchall()[0][0]

            cursor_like = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{cur[0]}' AND _type = True;")
            like_user_list = [row[0] for row in cursor_like.fetchall()]
            moment['is_current_user_like'] = current_user in like_user_list
            moment['like_nums'] = len(like_user_list)

            cursor_comment_nums = db.session.execute(f"SELECT COUNT(id) FROM comment WHERE moment_id = '{cur[0]}';")
            for _cur in cursor_comment_nums:
                moment['comment_nums'] = _cur[0]
            moments.append(moment)
        return True, moments
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_new_moment(current_user, base_id):
    try:        
        status, followings_list = db_get_followings(current_user)
        followings_list = [user['username'] for user in followings_list]
        print("following list: ", followings_list)
        if base_id != '':
            cursor = db.session.execute(f"SELECT id, username, title, content, img_nums, tag, location, time, _type FROM moment WHERE id < {base_id} ORDER BY id DESC LIMIT 10;")
        else:
            cursor = db.session.execute(f"SELECT id, username, title, content, img_nums, tag, location, time, _type FROM moment ORDER BY id DESC LIMIT 10;")
        moments = []
        status, res = db_get_user_blacklist(current_user)
        if not status:
            return False, res
        for cur in cursor:
            if cur[1] in res:
                continue  # 在黑名单
            status, _res = db_get_nickname(cur[1])
            if not status:
                return False, _res
            if str(cur[8]) == '0':
                mp4url = ''
            else:
                mp4url = 'http://129.211.216.10:5001/static/moment_imgs/' + str(cur[0]) + '_1.mp4'
            moment = {'id': cur[0], 'username': cur[1], 'nickname': _res, 'title': cur[2], 'content': cur[3], 'img_nums': cur[4], 'tag': cur[5], 'location':cur[6], 'time': format_time(cur[7]), 'mp4url': mp4url}
            cursor_star = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{cur[0]}' AND _type = False;")
            moment['avatar'] = db.session.execute(f"SELECT avatar FROM users WHERE username = '{moment['username']}';").fetchall()[0][0]
            star_user_list = [row[0] for row in cursor_star.fetchall()]
            moment['is_current_user_star'] = current_user in star_user_list
            moment['star_nums'] = len(star_user_list)
            
            moment['is_current_user_following'] = cur[1] in followings_list

            cursor_like = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{cur[0]}' AND _type = True;")
            like_user_list = [row[0] for row in cursor_like.fetchall()]
            moment['is_current_user_like'] = current_user in like_user_list
            moment['like_nums'] = len(like_user_list)

            cursor_comment_nums = db.session.execute(f"SELECT COUNT(id) FROM comment WHERE moment_id = '{cur[0]}';")
            for _cur in cursor_comment_nums:
                moment['comment_nums'] = _cur[0]
            moments.append(moment)
        return True, moments
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_user_star_moment_id_list(username):
    try:
        cursor = db.session.execute(f"SELECT moment_id FROM like_and_star WHERE username = '{username}' AND _type = False")
        star_moment_id_list = [cur[0] for cur in cursor]
        return True, star_moment_id_list
    except Exception as e:
        print(str(e))
        return False, str(e)
    

def db_get_moment_by_id(username, moment_id):
    try:
        status, followings_list = db_get_followings(username)
        followings_list = [user['username'] for user in followings_list]
        cursor = db.session.execute(f"SELECT id, username, title, content, img_nums, tag, location, time, _type FROM moment WHERE id = '{moment_id}';")
        moment = {}
        for cur in cursor:
            status, _res = db_get_nickname(cur[1])
            if not status:
                return False, _res
            if str(cur[8]) == '0':
                mp4url = ''
            else:
                mp4url = 'http://129.211.216.10:5001/static/moment_imgs/' + str(cur[0]) + '_1.mp4'
            moment = {'id': cur[0], 'username': cur[1], 'nickname': _res, 'title': cur[2], 'content': cur[3], 'img_nums': cur[4], 'tag': cur[5], 'location':cur[6], 'time': format_time(cur[7]), 'mp4url': mp4url}
            cursor_star = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{cur[0]}' AND _type = False;")
            star_user_list = [row[0] for row in cursor_star.fetchall()]
            moment['is_current_user_star'] = username in star_user_list
            moment['star_nums'] = len(star_user_list)

            moment['is_current_user_following'] = cur[1] in followings_list

            cursor_like = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{cur[0]}' AND _type = True;")
            like_user_list = [row[0] for row in cursor_like.fetchall()]
            moment['is_current_user_like'] = username in like_user_list
            moment['like_nums'] = len(like_user_list)
            moment['avatar'] = db.session.execute(f"SELECT avatar FROM users WHERE username = '{moment['username']}';").fetchall()[0][0]

            cursor_comment_nums = db.session.execute(f"SELECT COUNT(id) FROM comment WHERE moment_id = '{cur[0]}';")
            for _cur in cursor_comment_nums:
                moment['comment_nums'] = _cur[0]
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
        db.session.execute(f"DELETE FROM like_and_star WHERE moment_id = '{moment_id}' AND username ='{username}' AND _type = False;")
        db.session.commit()
        return True, "success"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_user_like_moment_id_list(username):
    try:
        cursor = db.session.execute(f"SELECT moment_id FROM like_and_star WHERE username = '{username}' AND _type = True")
        like_moment_id_list = [cur[0] for cur in cursor]
        return True, like_moment_id_list
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_like_moment(username, moment_id):
    try:
        status, res = db_get_user_like_moment_id_list(username)
        if not status:
            return False, res
        if moment_id in res:
            return False, "the moment has been liked by the user"
        like_and_star = LikeAndStar(moment_id=moment_id, _type=True, username=username)
        db.session.add(like_and_star)
        db.session.commit()
        return True, "success"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_unlike_moment(username, moment_id):
    try:
        status, res = db_get_user_like_moment_id_list(username)
        if not status:
            return False, res
        if moment_id not in res:
            return False, "the moment has not been liked by the user"
        db.session.execute(f"DELETE FROM like_and_star WHERE moment_id = '{moment_id}' AND username ='{username}' AND _type = True;")
        db.session.commit()
        return True, "success"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_followings_moment(username, base_id, filter):
    try:
        
        status, followings_list = db_get_followings(username)
        followings_list = [user['username'] for user in followings_list]
        status, res = db_get_followings(username)
        if not status:
            return False, res
        moments = []
        status, _res = db_get_user_blacklist(username)
        if not status:
            return False, _res
        for following in res:
            if following['username'] in _res:
                continue  # 在黑名单
            status, __res = db_get_nickname(following['username'])
            if not status:
                return False, __res
            cursor = db.session.execute(f"SELECT id, username, title, content, img_nums, tag, location, time, _type FROM moment WHERE username = '{following['username']}' ORDER BY id DESC;")
            for cur in cursor:
                if str(cur[8]) == '0':
                    mp4url = ''
                else:
                    mp4url = 'http://129.211.216.10:5001/static/moment_imgs/' + str(cur[0]) + '_1.mp4'
                moment = {'id': cur[0], 'username': cur[1], 'nickname': __res, 'title': cur[2], 'content': cur[3], 'img_nums': cur[4], 'tag': cur[5], 'location':cur[6], 'time': format_time(cur[7]), 'mp4url': mp4url}
                cursor_star = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{cur[0]}' AND _type = False;")
                star_user_list = [row[0] for row in cursor_star.fetchall()]
                moment['is_current_user_star'] = username in star_user_list
                moment['star_nums'] = len(star_user_list)
                moment['avatar'] = db.session.execute(f"SELECT avatar FROM users WHERE username = '{moment['username']}';").fetchall()[0][0]

                moment['is_current_user_following'] = cur[1] in followings_list

                cursor_like = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{cur[0]}' AND _type = True;")
                like_user_list = [row[0] for row in cursor_like.fetchall()]
                moment['is_current_user_like'] = username in like_user_list
                moment['like_nums'] = len(like_user_list)

                cursor_comment_nums = db.session.execute(f"SELECT COUNT(id) FROM comment WHERE moment_id = '{cur[0]}';")
                for _cur in cursor_comment_nums:
                    moment['comment_nums'] = _cur[0]
                moments.append(moment)
        if filter == 'like':
            moments = sorted(moments, key=lambda k: k['like_nums'], reverse=True)
        elif filter == 'comment':
            moments = sorted(moments, key=lambda k: k['comment_nums'], reverse=True)
        if base_id == '':
            return True, moments[:10]
        for index, moment in enumerate(moments):
            if int(base_id) == moment['id']:
                return True, moments[index + 1 : index + 11]
        return False, 'invalid base_id'
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_hot_moment(current_user, base_id):
    try:
        # 计算每个moment的点赞数和评论数
        like_counts = db.session.query(LikeAndStar.moment_id, func.count(LikeAndStar.id).label('count')).filter(LikeAndStar._type == True).group_by(LikeAndStar.moment_id).subquery()
        comment_counts = db.session.query(Comment.moment_id, func.count(Comment.id).label('count')).group_by(Comment.moment_id).subquery()

        # 计算每个moment的发布时间距离现在的时间
        now = datetime.datetime.now()
        time_difference = db.session.query(
            Moment.id, 
            (func.strftime('%d', now) - func.strftime('%d', Moment.time)).label('timediff')
        ).subquery()

        # 对点赞数、评论数和发布时间进行加权计算

        weighted_counts = db.session.query(
            Moment.id.label('id'), 
            (((like_counts.c.count * 0.5 + comment_counts.c.count * 0.5) / (time_difference.c.timediff + 1))).label('weighted_count')
         ).outerjoin(like_counts, Moment.id == like_counts.c.moment_id)    \
        .outerjoin(comment_counts, Moment.id == comment_counts.c.moment_id)  \
        .join(time_difference, Moment.id == time_difference.c.id)   \
        .subquery()


        # 获取按加权计算结果排列的动态列表
        top_moments = db.session.query(Moment).join(weighted_counts, Moment.id == weighted_counts.c.id).order_by(weighted_counts.c.weighted_count.desc()).all()
        if base_id == '':
            top_moments = top_moments[:10]
        else:
            for index, moment in enumerate(top_moments):
                if int(base_id) == moment.id:
                    top_moments = top_moments[index + 1 : index + 11]
                    base_id = ''
                    break
        
        if base_id != '':
            return False, 'invalid base_id'
        moments = []

        status, res = db_get_user_blacklist(current_user)
        
        status, followings_list = db_get_followings(current_user)
        followings_list = [user['username'] for user in followings_list]
        if not status:
            return False, res
        for moment in top_moments:
            if moment.username in res:
                continue  # 在黑名单
            status, _res = db_get_nickname(moment.username)
            if not status:
                return False, _res
            moment_dict = {
                'id': moment.id,
                'username': moment.username,
                'nickname': _res,
                'title': moment.title,
                'content': moment.content,
                'img_nums': moment.img_nums,
                'tag': moment.tag,
                'location': moment.location,
                'time': format_time(moment.time),
            }
            
            if str(moment._type) == '0':
                moment_dict['mp4url'] = ''
            else:
                moment_dict['mp4url'] = 'http://129.211.216.10:5001/static/moment_imgs/' + str(moment.id) + '_1.mp4'
            cursor_star = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{moment.id}' AND _type = False;")
            star_user_list = [row[0] for row in cursor_star.fetchall()]
            moment_dict['is_current_user_star'] = current_user in star_user_list
            moment_dict['star_nums'] = len(star_user_list)
            moment_dict['avatar'] = db.session.execute(f"SELECT avatar FROM users WHERE username = '{moment_dict['username']}';").fetchall()[0][0]

            moment_dict['is_current_user_following'] = moment.username in followings_list

            cursor_like = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{moment.id}' AND _type = True;")
            like_user_list = [row[0] for row in cursor_like.fetchall()]
            moment_dict['is_current_user_like'] = current_user in like_user_list
            moment_dict['like_nums'] = len(like_user_list)

            cursor_comment_nums = db.session.execute(f"SELECT COUNT(id) FROM comment WHERE moment_id = '{moment.id}';")
            for _cur in cursor_comment_nums:
                moment_dict['comment_nums'] = _cur[0]
            moments.append(moment_dict)
        return True, moments
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_tag_moment(current_user, base_id, filter, tag):
    try:
        status, followings_list = db_get_followings(current_user)
        followings_list = [user['username'] for user in followings_list]
        cursor = db.session.execute(f"SELECT id, username, title, content, img_nums, tag, location, time, _type FROM moment WHERE tag = '{tag}' ORDER BY id DESC;")
        moments = []
        status, res = db_get_user_blacklist(current_user)
        if not status:
            return False, res
        for cur in cursor:
            if cur[1] in res:
                continue  # 在黑名单
            status, _res = db_get_nickname(cur[1])
            if not status:
                return False, _res
            if str(cur[8]) == '0':
                mp4url = ''
            else:
                mp4url = 'http://129.211.216.10:5001/static/moment_imgs/' + str(cur[0]) + '_1.mp4'
            moment = {'id': cur[0], 'username': cur[1], 'nickname': _res, 'title': cur[2], 'content': cur[3], 'img_nums': cur[4], 'tag': cur[5], 'location':cur[6], 'time': format_time(cur[7]), 'mp4url': mp4url}
            cursor_star = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{cur[0]}' AND _type = False;")
            star_user_list = [row[0] for row in cursor_star.fetchall()]
            moment['is_current_user_star'] = current_user in star_user_list
            moment['star_nums'] = len(star_user_list)
            moment['avatar'] = db.session.execute(f"SELECT avatar FROM users WHERE username = '{moment['username']}';").fetchall()[0][0]

            moment['is_current_user_following'] = cur[1] in followings_list

            cursor_like = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{cur[0]}' AND _type = True;")
            like_user_list = [row[0] for row in cursor_like.fetchall()]
            moment['is_current_user_like'] = current_user in like_user_list
            moment['like_nums'] = len(like_user_list)

            cursor_comment_nums = db.session.execute(f"SELECT COUNT(id) FROM comment WHERE moment_id = '{cur[0]}';")
            for _cur in cursor_comment_nums:
                moment['comment_nums'] = _cur[0]
            moments.append(moment)
        if filter == 'like':
            moments = sorted(moments, key=lambda k: k['like_nums'], reverse=True)
        elif filter == 'comment':
            moments = sorted(moments, key=lambda k: k['comment_nums'], reverse=True)
        if base_id == '':
            return True, moments[:10]
        for index, moment in enumerate(moments):
            if int(base_id) == moment['id']:
                return True, moments[index + 1 : index + 11]
        return False, 'invalid base_id'
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_search_moment(current_user, key_words, base_id):
    try:
        
        status, followings_list = db_get_followings(current_user)
        followings_list = [user['username'] for user in followings_list]
        key_words = key_words.split(' ')
        #results = []
        #for key_word in key_words:
        #    results = results + Moment.query.filter(or_(
        #        Moment.title.contains(key_word),
        #        Moment.tag.contains(key_word),
        #        Moment.content.contains(key_word),
        #        Moment.username.contains(key_word)
        #    )).all()
        conditions = [or_(Moment.username.ilike(f'%{keyword}%'), Moment.title.ilike(f'%{keyword}%'), Moment.content.ilike(f'%{keyword}%'), Moment.tag.ilike(f'%{keyword}%')) for keyword in key_words]
        combined_condition = and_(*conditions)
        query = db.session.query(Moment).filter(combined_condition)
        results = query.all()
        results = sorted(results, key=lambda k: k.id, reverse=True)
        print(results)
        if base_id == '':
            results = results
        else:
            for index, moment in enumerate(results):
                if int(base_id) == moment.id:
                    results = results[index + 1 : index + 11]
                    base_id = ''
                    break
        if base_id != '':
            return False, 'invalid base_id'
            
        results = [{k: v for k, v in moment.__dict__.items() if k != '_sa_instance_state'} for moment in results]
        for moment in results:
            status, _res = db_get_nickname(moment['username'])
            if not status:
                return False, _res
            moment['nickname'] = _res
            if str(moment['_type']) == '0':
                mp4url = ''
            else:
                mp4url = 'http://129.211.216.10:5001/static/moment_imgs/' + str(moment['id']) + '_1.mp4'
            moment['mp4url'] = mp4url
            cursor_star = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{moment['id']}' AND _type = False;")
            star_user_list = [row[0] for row in cursor_star.fetchall()]
            moment['is_current_user_star'] = current_user in star_user_list
            moment['star_nums'] = len(star_user_list)
            moment['avatar'] = db.session.execute(f"SELECT avatar FROM users WHERE username = '{moment['username']}';").fetchall()[0][0]

            moment['is_current_user_following'] = moment['username'] in followings_list

            cursor_like = db.session.execute(f"SELECT username FROM like_and_star WHERE moment_id = '{moment['id']}' AND _type = True;")
            like_user_list = [row[0] for row in cursor_like.fetchall()]
            moment['is_current_user_like'] = current_user in like_user_list
            moment['like_nums'] = len(like_user_list)

            cursor_comment_nums = db.session.execute(f"SELECT COUNT(id) FROM comment WHERE moment_id = '{moment['id']}';")
            for _cur in cursor_comment_nums:
                moment['comment_nums'] = _cur[0]
        return True, results
    except Exception as e:
        print(str(e))
        return False, str(e)

def db_add_new_comment(username, moment_id, content):
    try:
        comment = Comment(username=username, moment_id=moment_id, content=content, time=datetime.datetime.now())
        db.session.add(comment)
        db.session.commit()
        return True, ''
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_comment(moment_id):
    try:
        cursor = db.session.execute(f"SELECT id, moment_id, username, content, time FROM comment WHERE moment_id = '{moment_id}' ORDER BY id;")
        comments = []
        for cur in cursor:
            status, _res = db_get_nickname(cur[2])
            if not status:
                return False, _res
            comment = {'id': cur[0], 'moment_id': cur[1], 'username': cur[2], 'nickname': _res, 'content': cur[3], 'time': format_time(cur[4])}
            comment['avatar'] = db.session.execute(f"SELECT avatar FROM users WHERE username = '{comment['username']}';").fetchall()[0][0]
            comments.append(comment)
        return True, comments
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_del_comment(username, comment_id):
    try:
        cursor = db.session.execute(f"SELECT username FROM comment WHERE id = '{comment_id}';")
        for cur in cursor:
            if username == cur[0]:
                db.session.execute(f"DELETE FROM comment WHERE id = '{comment_id}';")
                db.session.commit()
                return True, ''
            return False, 'user error'
        return False, 'no such comment'
    except Exception as e:
        print(str(e))
        return False, str(e)

def db_get_chatter(user):
    try:
        cursor = db.session.execute(f"SELECT username_1, username_2 FROM message WHERE username_1 = '{user}' OR username_2 = '{user}';")
        # get last message
        
        res_list = []
        chatter_list = []
        for cur in cursor:
            if cur[0] == user:
                cur_user = cur[1]
            else:
                cur_user = cur[0]
            if cur_user in chatter_list:
                continue
            chatter_list.append(cur_user)
            cursor1 = db.session.execute(f"SELECT username_1, username_2, content, time FROM message WHERE (username_1 = '{cur_user}' AND username_2 = '{user}') OR (username_2 = '{cur_user}' AND username_1 = '{user}') ORDER BY id DESC;")
            res_list.append({'username': cur_user, 'avatar': db.session.execute(f"SELECT avatar FROM users WHERE username = '{cur_user}';").fetchall()[0][0], 'last_message': cursor1.fetchall()[0][2]})
        # chatter_list = list(set(chatter_list))
        print(res_list)
        return True, res_list
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_add_new_message(current_user, target_user, content):
    try:
        print("sender", current_user, "receiver", target_user, content)
        message = Message(username_1=current_user, username_2=target_user, content=content, time=datetime.datetime.now())
        db.session.add(message)
        db.session.commit()
        return True, ''
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_message(current_user, target_user, base, direction):
    try:
        if base == '':
            cursor = db.session.execute(f"SELECT id, username_1, username_2, content, time FROM message WHERE (username_1 = '{current_user}' AND username_2 = '{target_user}') OR (username_2 = '{current_user}' AND username_1 = '{target_user}') ORDER BY id DESC LIMIT 10;")
        elif direction == 'old':
            cursor = db.session.execute(f"SELECT id, username_1, username_2, content, time FROM message WHERE id < {base} AND ((username_1 = '{current_user}' AND username_2 = '{target_user}') OR (username_2 = '{current_user}' AND username_1 = '{target_user}')) ORDER BY id DESC LIMIT 5;")
        else:
            cursor = db.session.execute(f"SELECT id, username_1, username_2, content, time FROM message WHERE id > {base} AND ((username_1 = '{current_user}' AND username_2 = '{target_user}') OR (username_2 = '{current_user}' AND username_1 = '{target_user}')) ORDER BY id LIMIT 5;")
        messages = []
        avatar_dict = { current_user: db_get_user_info(current_user)[1]['avatar'], target_user: db_get_user_info(target_user)[1]['avatar']}
        
        for cur in cursor:
            message = {'id': cur[0], 'sender': cur[1], 'receiver': cur[2], 'content': cur[3], 'time': format_time(cur[4]), 'avatar': avatar_dict[cur[1]]}
            messages.append(message)
        if base == '' or direction == 'old':
            messages.reverse()
        print(len(messages))
        return True, messages
    except Exception as e:
        print(str(e))
        return False, str(e)


def format_time(_time) -> str:
    if isinstance(_time, str):
        time = parser.parse(_time).strftime('%Y-%-m-%-d %H:%M')
    elif isinstance(_time, datetime.datetime):
        time = _time.strftime('%Y-%-m-%-d %H:%M')
    else:
        time = ""
    return time


def db_add_notice(sender, receiver, content, _type):
    try:
        first_img = ''
        if _type != '0':
            cursor = db.session.execute(f"SELECT img_nums FROM moment WHERE id = {content};")
            for cur in cursor:
                if str(cur[0]) != '0':
                    first_img = 'http://129.211.216.10:5001/static/moment_imgs/' + str(content) + '_1.jpg'
        notice = Notice(sender=sender, receiver=receiver, content=content, _type=_type, has_noticed=False, has_noticed_system=False, first_img=first_img, time=datetime.datetime.now())
        db.session.add(notice)
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False


def db_get_notice(username):
    try:
        cursor = db.session.execute(f"SELECT sender, receiver, content, _type, has_noticed, first_img, time FROM notice WHERE receiver = '{username}';")
        notices = []
        for cur in cursor:
            avatar = db.session.execute(f"SELECT avatar FROM users WHERE username = '{cur[0]}';").fetchall()[0][0]
            status, res = db_get_nickname(cur[0])
            if not status:
                return False, res
            notices.append({'sender': cur[0], 'receiver': cur[1], 'content': cur[2], '_type': cur[3], 'sender_avatar': avatar, 'sender_nickname': res, 'has_noticed': cur[4], 'first_img': cur[5], 'time': format_time(cur[6])})
        db.session.execute(f"UPDATE notice SET has_noticed = True WHERE receiver = '{username}';")
        db.session.commit()
        return True, notices
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_notice_system(username):
    try:
        cursor = db.session.execute(f"SELECT sender, receiver, content, _type, first_img, time FROM notice WHERE receiver = '{username}' AND has_noticed_system = False;")
        notices = []
        for cur in cursor:
            avatar = db.session.execute(f"SELECT avatar FROM users WHERE username = '{cur[0]}';").fetchall()[0][0]
            status, res = db_get_nickname(cur[0])
            if not status:
                return False, res
            notices.append({'sender': cur[0], 'receiver': cur[1], 'content': cur[2], '_type': cur[3], 'sender_avatar': avatar, 'sender_nickname': res, 'first_img': cur[4], 'time': format_time(cur[5]), "has_noticed": 0})
        db.session.execute(f"UPDATE notice SET has_noticed_system = True WHERE receiver = '{username}';")
        db.session.commit()
        return True, notices
    except Exception as e:
        print(str(e))
        return False, str(e)
