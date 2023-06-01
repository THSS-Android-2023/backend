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
    sender = identify(request.headers.get("Authorization", default=None))
    status, res = db_add_new_message(sender, body_data['target_user'], body_data['content'])
    if status:
        if db_add_notice(sender, body_data['target_user'], body_data['content'], '0'):
            return 'success', 200
        return 'add notice failed', 500
    return res, 500


@chat_bp.route('/get_message/<target_user>/', defaults={'base': '', 'direction': 'new'}, methods=['GET'])
@chat_bp.route('/get_message/<target_user>/<base>/<direction>/', methods=['GET'])
@swag_from('swagger/getMessage.yml')
@login_required
def api_get_message(target_user, base, direction):
    if base != '' and int(base) < 0:
        return 'invalid base', 400
    if str(direction) not in ['new', 'old']:
        return 'invalid direction', 400
    status, res = db_get_message(identify(request.headers.get("Authorization", default=None)), target_user, base, direction)
    if status:
        return jsonify(res), 200
    return res, 500
