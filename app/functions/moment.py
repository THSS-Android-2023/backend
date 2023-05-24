import datetime
import os

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from werkzeug.utils import secure_filename

from app.functions.database import *
from app.functions.account import login_required, identify


moment_bp = Blueprint("moment", __name__)


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
        status, res = db_add_new_moment(identify(request.headers.get("Authorization", default=None)), body_data['title'], body_data['content'], img_nums, tag)
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
        status, res = db_add_new_moment(identify(request.headers.get("Authorization", default=None)), body_data['title'], body_data['content'], 0, tag)
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
