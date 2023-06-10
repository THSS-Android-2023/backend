import os
from PIL import Image

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
    tag = request.form.get('tag', '')
    if tag not in tag_map.keys():
        print('tag')
        return 'unsupport tag', 400
    if 'files[]' in request.files:    
        files = request.files.getlist('files[]')
        img_nums = len(files)
        print(files)
        index = 0
        for file in files:
            if file.filename == '':
                print('No selected file')
                return 'No selected file', 400
            filename = secure_filename(file.filename)
            file_ext = filename.split('.')[-1].lower()

            if file_ext not in ['jpg', 'png', 'mp4']:
                print('unsupport file type')
                return 'unsupport file type', 400
            if file_ext == 'mp4':
                status, res = db_add_new_moment(identify(request.headers.get("Authorization", default=None)), request.form.get('title', ''), request.form.get('content', ''), 0, tag, request.form.get('location', ''), 1)
                if not status:
                    return res, 500
                filename = str(res) + '_1.mp4'
                directory = '~/djk/backend/app/static/moment_imgs/'
                directory = os.path.expanduser(directory)
                os.makedirs(directory, exist_ok=True)
                filepath = os.path.join(directory, filename)
                file.save(filepath)
            else:
                status, res = db_add_new_moment(identify(request.headers.get("Authorization", default=None)), request.form.get('title', ''), request.form.get('content', ''), img_nums, tag, request.form.get('location', ''), 0)
                if not status:
                    return res, 500
                
                for file in files:
                    index = index + 1
                    if file.filename == '':
                        print('No selected file')
                        return 'No selected file', 400
                    filename = secure_filename(file.filename)
                    file_ext = filename.split('.')[-1].lower()

                    if file_ext not in ['jpg', 'png']:
                        print('unsupport file type')
                        return 'unsupport file type', 400
                    filename = str(res) + '_' + str(index) + '.' + file_ext

                    # 将PNG转换为JPG
                    if file_ext == 'png':
                        img = Image.open(file)
                        jpg_filename = filename.rsplit('.', 1)[0] + '.jpg'
                        img = img.convert('RGB')
                        save_directory = os.path.expanduser('~/djk/backend/app/static/moment_imgs/')
                        save_path = os.path.join(save_directory, jpg_filename)
                        img.save(save_path, 'JPEG')
                        continue
            
                    directory = '~/djk/backend/app/static/moment_imgs/'
                    directory = os.path.expanduser(directory)
                    os.makedirs(directory, exist_ok=True)
                    filepath = os.path.join(directory, filename)
                    file.save(filepath)
            return str(res), 200
    else:
        print("No img")
        status, res = db_add_new_moment(identify(request.headers.get("Authorization", default=None)), request.form.get('title', ''), request.form.get('content', ''), 0, tag, request.form.get('location', ''), 0)
        if status:
            return str(res), 200
        return res, 500


@moment_bp.route('/get_moment/<username>/', defaults={'base_id': ''}, methods=['GET'])
@moment_bp.route('/get_moment/<username>/<base_id>/', methods=['GET'])
@swag_from('swagger/getMoment.yml')
@login_required
def api_get_user_moment(username, base_id):
    if base_id != '' and int(base_id) < 0:
        return 'invalid base_id', 400
    status, res = db_get_user_moment(identify(request.headers.get("Authorization", default=None)), username, base_id)
    if status:
        print(res)
        return jsonify(res), 200
    return res, 500

@moment_bp.route('/get_moment_by_id/<base_id>/', methods=['GET'])
@swag_from('swagger/getMomentById.yml')
@login_required
def api_get_user_moment_by_id(base_id):
    base_id = int(base_id)
    if base_id < 0:
        return 'invalid base_id', 400
    status, res = db_get_moment_by_id(identify(request.headers.get("Authorization", default=None)), base_id)
    if status:
        print(res)
        return jsonify(res), 200
    return res, 500


@moment_bp.route('/star_moment/', methods=['POST'])
@swag_from('swagger/starMoment.yml')
@login_required
def api_star_moment():
    body_json = request.json
    status, message = db_star_moment(identify(request.headers.get("Authorization", default=None)), int(body_json['moment_id']))
    if status:
        return 'success', 200
    return message, 500


@moment_bp.route('/unstar_moment/', methods=['POST'])
@swag_from('swagger/unstarMoment.yml')
@login_required
def api_unstar_moment():
    body_json = request.json
    status, message = db_unstar_moment(identify(request.headers.get("Authorization", default=None)), int(body_json['moment_id']))
    if status:
        return 'success', 200
    return message, 500


@moment_bp.route('/get_star_moment/', defaults={'base_id': ''}, methods=['GET'])
@moment_bp.route('/get_star_moment/<base_id>/', methods=['GET'])
@swag_from('swagger/getStarMoment.yml')
@login_required
def api_get_star_moment(base_id):
    if base_id != '' and int(base_id) < 0:
        return 'invalid base_id', 400
    username = identify(request.headers.get("Authorization", default=None))
    status, res = db_get_user_star_moment_id_list(username)
    if not status:
        return res, 500
    target_moment_id_list = [moment for moment in res if base_id == '' or moment < int(base_id)]
    target_moment_id_list = target_moment_id_list[:10]
    moments = []
    for moment_id in target_moment_id_list:
        status, res = db_get_moment_by_id(username, moment_id)
        if not status:
            return res, 500
        moments.append(res)
    print(moments)
    return jsonify(moments), 200


@moment_bp.route('/like_moment/', methods=['POST'])
@swag_from('swagger/likeMoment.yml')
@login_required
def api_like_moment():
    body_json = request.json
    current_user = identify(request.headers.get("Authorization", default=None))
    status, message = db_like_moment(current_user, int(body_json['moment_id']))
    if status:
        status, res = db_get_moment_by_id(current_user, int(body_json['moment_id']))
        if status:
            status = db_add_notice(current_user, res['username'], body_json['moment_id'], '1')
            if status:
                return 'success', 200
            return 'add notice failed', 500
        return res, 500
    return message, 500


@moment_bp.route('/unlike_moment/', methods=['POST'])
@swag_from('swagger/unlikeMoment.yml')
@login_required
def api_unlike_moment():
    body_json = request.json
    status, message = db_unlike_moment(identify(request.headers.get("Authorization", default=None)), int(body_json['moment_id']))
    if status:
        return 'success', 200
    return message, 500


@moment_bp.route('/get_new_moment/', defaults={'base_id': ''}, methods=['GET'])
@moment_bp.route('/get_new_moment/<base_id>/', methods=['GET'])
@swag_from('swagger/getNewMoment.yml')
@login_required
def api_get_new_moment(base_id):
    if base_id != '' and int(base_id) < 0:
        return 'invalid base_id', 400
    status, res = db_get_new_moment(identify(request.headers.get("Authorization", default=None)), base_id)
    if status:
        return jsonify(res), 200
    return res, 500


@moment_bp.route('/get_followings_moment/<filter>/', defaults={'base_id': ''}, methods=['GET'])
@moment_bp.route('/get_followings_moment/<filter>/<base_id>/', methods=['GET'])
@swag_from('swagger/getFollowingsMoment.yml')
@login_required
def api_get_followings_moment(filter, base_id):
    if base_id != '' and int(base_id) < 0:
        return 'invalid base_id', 400
    if str(filter) not in ['time', 'like', 'comment']:
        return 'invalid filter', 400
    filter = str(filter)
    status, res = db_get_followings_moment(identify(request.headers.get("Authorization", default=None)), base_id, filter)
    if status:
        return jsonify(res), 200
    return res, 500

@moment_bp.route('/get_hot_moment/', defaults={'base_id': ''}, methods=['GET'])
@moment_bp.route('/get_hot_moment/<base_id>/', methods=['GET'])
@swag_from('swagger/getHotMoment.yml')
@login_required
def api_get_hot_moment(base_id):
    if base_id != '' and int(base_id) < 0:
        return 'invalid base_id', 400
    status, res = db_get_hot_moment(identify(request.headers.get("Authorization", default=None)), base_id)
    if status:
        return jsonify(res), 200
    print(res)
    return res, 500

@moment_bp.route('/get_tag_moment/<tag>/<filter>/', defaults={'base_id': ''}, methods=['GET'])
@moment_bp.route('/get_tag_moment/<tag>/<filter>/<base_id>/', methods=['GET'])
@swag_from('swagger/getTagMoment.yml')
@login_required
def api_get_tag_moment(tag, filter, base_id):
    if base_id != '' and int(base_id) < 0:
        return 'invalid base_id', 400
    if str(filter) not in ['time', 'like', 'comment']:
        return 'invalid filter', 400
    if str(tag) not in ['xyzx', 'esjy', 'xxky', 'chwl']:
        return 'unsupport tag', 400
    status, res = db_get_tag_moment(identify(request.headers.get("Authorization", default=None)), base_id, filter, tag)
    if status:
        return jsonify(res), 200
    print(res)
    return res, 500


@moment_bp.route('/search_moment/<key_words>/', defaults={'base_id': ''}, methods=['GET'])
@moment_bp.route('/search_moment/<key_words>/<base_id>/', methods=['GET'])
@swag_from('swagger/searchMoment.yml')
@login_required
def api_search_moment(key_words, base_id):
    if base_id != '' and int(base_id) < 0:
        return 'invalid base_id', 400
    status, res = db_search_moment(identify(request.headers.get("Authorization", default=None)), key_words, base_id)
    if status:
        return jsonify(res), 200
    print(res)
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
