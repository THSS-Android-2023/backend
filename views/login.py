from .database import db_insertuser, db_verify_pw, db_deleteuser, db_selectUserByName, db_change_user_info, db_change_password, db_get_user_info, db_star_user, db_unstar_user
from flask import Blueprint, session, request, abort, jsonify
from functools import wraps

login_bp = Blueprint("login", __name__)

# This file contains login/logout/register-related part.

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            abort(401)  # 401 Unauthorized
        return view_func(*args, **kwargs)
    return wrapper

@login_bp.route('/', methods=["POST"])
def login():
    body_data = request.json
    if db_verify_pw(body_data["username"], body_data["password"]):
        session['username'] = body_data['username']
        return 'success', 200
    return 'failed', 401

# check if client is logged
@login_bp.get('/is_logged_in/')
@login_required
def check_logged_in():
    return session["username"], 200

# logout
@login_bp.get('/logout/')
def logout():
    session.pop('username', None)
    return 'success', 200

# register a user
@login_bp.route('/register/', methods=['POST', 'DELETE'])
def register():
    body_json = request.json
    if request.method == 'POST':
        if db_selectUserByName(body_json["username"]):
            return 'duplicate username', 400
        if not db_insertuser(body_json["username"], body_json["password"]):
            return 'failed to register', 500
        else:
            return 'suceess', 201
    else:
        if not db_verify_pw(body_json["username"], body_json["password"]):
            return 'password wrong', 401
        if not db_deleteuser(body_json["username"], body_json["password"]):
            return 'failed to deregister', 500
        else:
            return 'suceess', 200


@login_bp.route('/change_info/', methods=['POST'])
# @login_required
def api_change_info():
    body_json = request.json
    print(body_json["username"], body_json["intro"], body_json["avatar"])
    status, message = db_change_user_info(body_json["username"], body_json["intro"], body_json["avatar"])
    if status:
        return 'success', 200
    return message, 500


@login_bp.route('/get_info/', methods=['GET'])
@login_required
def api_get_user_info():
    status, res = db_get_user_info(request.json['username'])
    if status:
        return jsonify({'intro': res[0], 'avatar': res[1], 'star_user_list': res[2]}), 200
    return res, 500


@login_bp.route('/change_password/', methods=['POST'])
def api_change_password():
    body_json = request.json
    status, message = db_change_password(body_json["username"], body_json["old_password"], body_json["new_password"])
    if status:
        return 'success', 200
    if message == "verify failed":
        return message, 400
    return message, 500


@login_bp.route('/star_user/', methods=['POST'])
@login_required
def api_star_user():
    body_json = request.json
    status, message = db_star_user(body_json['username'], body_json['target_username'])
    if status:
        return 'success', 200
    return message, 500


@login_bp.route('/unstar_user/', methods=['POST'])
@login_required
def api_unstar_user():
    body_json = request.json
    status, message = db_unstar_user(body_json['username'], str(body_json['target_username']))
    if status:
        return 'success', 200
    return message, 500