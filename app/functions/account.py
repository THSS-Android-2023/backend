import jwt
import datetime
import os

from flask import Blueprint, request, jsonify
from functools import wraps
from flasgger import swag_from
from werkzeug.utils import secure_filename

from app.functions.database import *


account_bp = Blueprint("account", __name__)

key = "123456"


def generate_access_token(username: str = "", algorithm: str = 'HS256', exp: float = 200000):
    """
    生成access_token
    :param username: 用户名(自定义部分)
    :param algorithm: 加密算法
    :param exp: 过期时间
    :return:token
    """

    now = datetime.datetime.utcnow()
    exp_datetime = now + datetime.timedelta(hours=exp)
    access_payload = {
        'exp': exp_datetime,
        'flag': 0,   # 标识是否为一次性token，0是，1不是
        'iat': now,   # 开始时间
        'iss': 'leon',   # 签名
        'username': username   # 用户名(自定义部分)
    }
    access_token = jwt.encode(access_payload, key, algorithm=algorithm)
    return access_token.decode()


def decode_auth_token(token: str):
    """
    解密token
    :param token:token字符串
    :return:
    """
    try:
        payload = jwt.decode(token, key=key, algorithms='HS256')
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.InvalidSignatureError):
        return ""
    else:
        return payload


def identify(auth_header: str):
    """
    用户鉴权
    """
    if auth_header:
        payload = decode_auth_token(auth_header)
        if not payload:
            return False
        if "username" in payload and "flag" in payload:
            if payload["flag"] == 0:
                return payload["username"]
            else:
                return False
    return False


def login_required(f):
    """
    登录保护，验证用户是否登录
    :param f:
    :return:
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", default=None)
        if not token:
            return 'not Login', 401
        username = identify(token)
        if not username:
            return 'not Login', 401      # return 响应体, 状态码, 响应头
        return f(*args, **kwargs)
    return wrapper


@account_bp.route('/is_logged_in/', methods=['GET'])
@swag_from('swagger/isLoggedIn.yml')
@login_required
def is_logged_in():
    return identify(request.headers.get("Authorization", default=None)), 200  # 成功通过login_required认证则返回username


@account_bp.route("/", methods=['POST'])
@swag_from('swagger/login.yml')
def login():
    # 登录，成功则返回200，否则返回401
    body_data = request.json
    username = body_data['username']
    password = body_data['password']
    if db_verify_user(username, password):
        return jsonify({'jwt': generate_access_token(username)}), 200
    return 'failed', 401


@account_bp.route("/register/", methods=['POST'])
@swag_from('swagger/register.yml')
def create_new_account():
    # 注册新的账号，成功则返回 'success' 及201，否则打印错误信息到后端控制台并返回给前端
    body_data = request.json
    username = body_data['username']
    if ' ' in username or username == 'default' or '%20' in username:
        return 'invalid username', 400
    password = body_data['password']
    # email = body_data['email']
    # verify_code = body_data['verify_code']
    # status, message = db_check_verify_code(verify_code, email)
    # if status is False:
    #    return message, 500
    if db_add_new_user(username, password):
        return 'success', 201
    return 'duplicate username', 400


@account_bp.route('/change_info/', methods=['POST'])
@swag_from('swagger/changeInfo.yml')
@login_required
def api_change_info():
    username = identify(request.headers.get("Authorization", default=None))    
    body_data = request.json
    if 'intro' in body_data and body_data['intro'] != '':
        intro = body_data['intro']
    else:
        intro = None
    if 'nickname' in body_data and body_data['nickname'] != '':
        nickname = body_data['nickname']
    else:
        nickname = None
    status = db_change_user_info(username, intro, nickname)
    if status:
        return 'success', 200
    return 'failed', 500


@account_bp.route('/change_avatar/', methods=['POST'])
@swag_from('swagger/changeAvatar.yml')
@login_required
def api_change_avatar():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    filename = secure_filename(file.filename)
    if filename.split('.')[-1].lower() not in ['jpg', 'png', 'jpeg', 'gif', 'bmp']:
        return 'unsupport file type', 400

    username = identify(request.headers.get("Authorization", default=None))
    filename = username + '.'+ filename.split('.')[-1]
    
    directory = '~/djk/backend/app/static/'
    directory = os.path.expanduser(directory)
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    file.save(filepath)
    url = 'http://129.211.216.10:5001/static/' + filename
    db_change_user_avatar(username, url)
    return url, 201


@account_bp.route('/get_info/', methods=['GET'])
@swag_from('swagger/getInfo.yml')
@login_required
def api_get_user_info():
    status, res = db_get_user_info(identify(request.headers.get("Authorization", default=None)))
    if status:
        return jsonify(res), 200
    return res, 500


@account_bp.route('/get_info/<username>/', methods=['GET'])
@swag_from('swagger/getOthersInfo.yml')
@login_required
def api_get_other_user_info(username):
    status, res = db_get_user_info(username)
    if status:
        status, res_2 = db_get_user_blacklist(identify(request.headers.get("Authorization", default=None)))
        if status:
            res['is_blacked'] = username in res_2
            status, res_3 = db_get_followings(identify(request.headers.get("Authorization", default=None)))
            if status:
                res['is_following'] = username in [u['username'] for u in res_3]
                print(res)
                return jsonify(res), 200
        return res_2, 500
    return res, 500


@account_bp.route("/change_password/", methods=['POST'])
@swag_from('swagger/changePassword.yml')
def api_change_password():
    # 修改密码，成功则返回 'success' 及201，否则打印错误信息到后端控制台并返回给前端
    body_json = request.json
    username = body_json['username']
    password = body_json['old_password']
    if db_verify_user(username, password):
        if db_change_user_password(username, body_json['new_password']):
            return 'success', 200
        return '服务器错误', 500
    return 'verify failed', 401


@account_bp.route('/follow_user/', methods=['POST'])
@swag_from('swagger/followUser.yml')
@login_required
def api_follow_user():
    body_json = request.json
    status, message = db_follow_user(identify(request.headers.get("Authorization", default=None)), body_json['target_username'])
    if status:
        return 'success', 200
    print(message)
    return message, 500


@account_bp.route('/check_followship/', methods=['GET'])
@swag_from('swagger/checkFollowship.yml')
@login_required
def api_check_followship():
    body_json = request.args
    status, message = db_check_followship(identify(request.headers.get("Authorization", default=None)), body_json['target_username'])
    if status:
        return jsonify([message]), 200
    return message, 500


@account_bp.route('/unfollow_user/', methods=['POST'])
@swag_from('swagger/unfollowUser.yml')
@login_required
def api_unfollow_user():
    body_json = request.json
    status, message = db_unfollow_user(identify(request.headers.get("Authorization", default=None)), str(body_json['target_username']))
    if status:
        return 'success', 200
    return message, 500


@account_bp.route('/get_following/', methods=['GET'])
@swag_from('swagger/getFollowing.yml')
@login_required
def api_get_following():
    status, message = db_get_followings(identify(request.headers.get("Authorization", default=None)))
    if status:
        return jsonify(message), 200
    return "failed", 500

@account_bp.route('/get_follower/', methods=['GET'])
@swag_from('swagger/getFollower.yml')
@login_required
def api_get_follower():
    status, message = db_get_followers(identify(request.headers.get("Authorization", default=None)))
    if status:
        return jsonify(message), 200
    return "failed", 500

@account_bp.route('/black_user/', methods=['POST'])
@swag_from('swagger/blackUser.yml')
@login_required
def api_black_user():
    body_json = request.json
    status, message = db_black_user(identify(request.headers.get("Authorization", default=None)), body_json['target_username'])
    if status:
        return 'success', 200
    return message, 500


@account_bp.route('/unblack_user/', methods=['POST'])
@swag_from('swagger/unblackUser.yml')
@login_required
def api_unblack_user():
    body_json = request.json
    status, message = db_unblack_user(identify(request.headers.get("Authorization", default=None)), str(body_json['target_username']))
    if status:
        return 'success', 200
    return message, 500
