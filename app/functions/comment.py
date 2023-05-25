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
