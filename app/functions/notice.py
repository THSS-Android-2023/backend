from flask import Blueprint, request, jsonify
from flasgger import swag_from

from app.functions.database import *
from app.functions.account import login_required, identify


notice_bp = Blueprint("notice", __name__)


@notice_bp.route('/get_notice/', methods=['GET'])
@swag_from('swagger/getNotice.yml')
@login_required
def api_get_notice():
    status, res = db_get_notice(identify(request.headers.get("Authorization", default=None)))
    if status:
        return jsonify(res), 200
    return res, 500
