from flask import Blueprint, request, jsonify
from flasgger import swag_from

from app.functions.database import *
from app.functions.account import login_required, identify


chat_bp = Blueprint("chat", __name__)


@chat_bp.route('/send_message/', methods=['POST'])
@swag_from('swagger/sendMessage.yml')
@login_required
def api_send_message():
    body_data = request.json
    status, res = db_add_new_message(identify(request.headers.get("Authorization", default=None)), body_data['target_user'], body_data['content'])
    if status:
        return 200, 'success'
    return 500, res


@chat_bp.route('/get_message/<target_user>/<base>/<direction>/', methods=['GET'])
@swag_from('swagger/getMessage.yml')
@login_required
def api_get_message(target_user, base, direction):
    if int(base) < 0:
        return 400, 'invalid base'
    if str(direction) not in ['new', 'old']:
        return 400, 'invalid direction'
    status, res = db_get_message(identify(request.headers.get("Authorization", default=None)), target_user, base, direction)
    if status:
        return 200, jsonify(res)
    return 500, res
