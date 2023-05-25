from flask import Blueprint, request, jsonify
from flasgger import swag_from

from app.functions.database import *
from app.functions.account import login_required, identify


comment_bp = Blueprint("comment", __name__)


@comment_bp.route('/publish_comment/', methods=['POST'])
@swag_from('swagger/publishComment.yml')
@login_required
def api_publish_a_new_comment():
    body_data = request.json
    status, res = db_add_new_comment(identify(request.headers.get("Authorization", default=None)), body_data['moment_id'], body_data['content'])
    if status:
        return 200, 'success'
    return 500, res


@comment_bp.route('/del_comment/', methods=['POST'])
@swag_from('swagger/delComment.yml')
@login_required
def api_del_comment():
    status, res = db_del_comment(identify(request.headers.get("Authorization", default=None)), request.json['comment_id'])
    if status:
        return 'success', 200
    if res == 'user error':
        return 'invalid user', 401
    return res, 500


@comment_bp.route('/get_comment/<moment_id>/', methods=['GET'])
@swag_from('swagger/getComment.yml')
@login_required
def api_get_comment(moment_id):
    status, res = db_get_comment(moment_id)
    if status:
        return jsonify(res), 200
    return res, 500
