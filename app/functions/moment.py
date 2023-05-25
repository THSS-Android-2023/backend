import os

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from werkzeug.utils import secure_filename

from app.functions.database import *
from app.functions.account import login_required, identify


moment_bp = Blueprint("moment", __name__)
tag_map = {'xyzx': '校园资讯', 'esjy': '二手交易', 'xxky': '学习科研', 'chwl': '吃喝玩乐'}


@moment_bp.route('/publish_moment/', methods=['POST'])
@swag_from('swagger/publishMoment.yml')
@login_required
def api_publish_a_new_moment():
    body_data = request.json
    tag = body_data['tag']
    if tag not in ['校园资讯', '二手交易', '学习科研', '吃喝玩乐']:
        return 'unsupport tag', 400
    if 'files[]' in request.files:    
        files = request.files.getlist('files[]')
        img_nums = len(files)
        status, res = db_add_new_moment(identify(request.headers.get("Authorization", default=None)), body_data['title'], body_data['content'], img_nums, tag, body_data['location'])
        if not status:
            return res, 500
        index = 0
        for file in files:
            index = index + 1
            if file.filename == '':
                return 'No selected file', 400
            filename = secure_filename(file.filename)
            if filename.split('.')[-1].lower() not in ['jpg', 'png', 'jpeg', 'gif', 'bmp', 'mp4', 'avi', 'webm']:
                return 'unsupport file type', 400
            
            filename = str(res) + '_' + str(index) + '.'+ filename.split('.')[-1]
    
            directory = '~/djk/backend/app/static/moment_imgs/'
            directory = os.path.expanduser(directory)
            os.makedirs(directory, exist_ok=True)
            filepath = os.path.join(directory, filename)
            file.save(filepath)
        return res, 200
    else:
        status, res = db_add_new_moment(identify(request.headers.get("Authorization", default=None)), body_data['title'], body_data['content'], 0, tag, body_data['location'])
        if status:
            return res, 200
        return res, 500


@moment_bp.route('/get_moment/<username>/<page>/', methods=['GET'])
@swag_from('swagger/getMoment.yml')
@login_required
def api_get_user_moment(username, page):
    if int(page) < 0:
        return 'invalid page', 400
    status, res = db_get_user_moment(identify(request.headers.get("Authorization", default=None)), username, page)
    if status:
        return jsonify(res), 200
    return res, 500


@moment_bp.route('/star_moment/', methods=['POST'])
@swag_from('swagger/starMoment.yml')
@login_required
def api_star_moment():
    body_json = request.json
    status, message = db_star_moment(identify(request.headers.get("Authorization", default=None)), body_json['moment_id'])
    if status:
        return 'success', 200
    return message, 500


@moment_bp.route('/unstar_moment/', methods=['POST'])
@swag_from('swagger/unstarMoment.yml')
@login_required
def api_unstar_moment():
    body_json = request.json
    status, message = db_unstar_moment(identify(request.headers.get("Authorization", default=None)), body_json['moment_id'])
    if status:
        return 'success', 200
    return message, 500


@moment_bp.route('/get_star_moment/<page>/', methods=['GET'])
@swag_from('swagger/getStarMoment.yml')
@login_required
def api_get_star_moment(page):
    if int(page) < 0:
        return 'invalid page', 400
    username = identify(request.headers.get("Authorization", default=None))
    status, res = db_get_user_star_moment_id_list(username)
    if not status:
        return res, 500
    target_moment_id_list = res[page * 10 : (page + 1) * 10]
    moments = []
    for moment_id in target_moment_id_list:
        status, res = db_get_moment_by_id(username, moment_id)
        if not status:
            return res, 500
        moments.append(res)
    return jsonify(moments), 200


@moment_bp.route('/like_moment/', methods=['POST'])
@swag_from('swagger/likeMoment.yml')
@login_required
def api_like_moment():
    body_json = request.json
    status, message = db_like_moment(identify(request.headers.get("Authorization", default=None)), body_json['moment_id'])
    if status:
        return 'success', 200
    return message, 500


@moment_bp.route('/unlike_moment/', methods=['POST'])
@swag_from('swagger/unlikeMoment.yml')
@login_required
def api_unlike_moment():
    body_json = request.json
    status, message = db_unlike_moment(identify(request.headers.get("Authorization", default=None)), body_json['moment_id'])
    if status:
        return 'success', 200
    return message, 500


@moment_bp.route('/get_new_moment/<page>/', methods=['GET'])
@swag_from('swagger/getNewMoment.yml')
@login_required
def api_get_new_moment(page):
    if int(page) < 0:
        return 'invalid page', 400
    status, res = db_get_new_moment(identify(request.headers.get("Authorization", default=None)), page)
    if status:
        return jsonify(res), 200
    return res, 500


@moment_bp.route('/get_followings_moment/<filter>/<page>/', methods=['GET'])
@swag_from('swagger/getFollowingsMoment.yml')
@login_required
def api_get_followings_moment(filter, page):
    if int(page) < 0:
        return 'invalid page', 400
    if str(filter) not in ['time', 'like', 'comment']:
        return 'invalid filter', 400
    status, res = db_get_followings_moment(identify(request.headers.get("Authorization", default=None)), page, filter)
    if status:
        return jsonify(res), 200
    return res, 500


@moment_bp.route('/get_hot_moment/<page>/', methods=['GET'])
@swag_from('swagger/getHotMoment.yml')
@login_required
def api_get_hot_moment(page):
    if int(page) < 0:
        return 'invalid page', 400
    status, res = db_get_hot_moment(identify(request.headers.get("Authorization", default=None)), page)
    if status:
        return jsonify(res), 200
    return res, 500


@moment_bp.route('/get_tag_moment/<tag>/<filter>/<page>/', methods=['GET'])
@swag_from('swagger/getTagMoment.yml')
@login_required
def api_get_tag_moment(tag, filter, page):
    if int(page) < 0:
        return 'invalid page', 400
    if str(filter) not in ['time', 'like', 'comment']:
        return 'invalid filter', 400
    if str(tag) not in ['xyzx', 'esjy', 'xxky', 'chwl']:
        return 'unsupport tag', 400
    tag = tag_map[tag]
    status, res = db_get_tag_moment(identify(request.headers.get("Authorization", default=None)), page, filter, tag)
    if status:
        return jsonify(res), 200
    return res, 500


@moment_bp.route('/del_moment/', methods=['POST'])
@swag_from('swagger/delMoment.yml')
@login_required
def api_del_moment():
    status, res = db_del_moment(identify(request.headers.get("Authorization", default=None)), request.json['moment_id'])
    if status:
        return 'success', 200
    if res == 'user error':
        return 'invalid user', 401
    return res, 500
