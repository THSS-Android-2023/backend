from flask import Flask
from flask_cors import CORS

from app.extensions.extensions import db, swagger

from app.functions.account import account_bp
from app.functions.moment import moment_bp
from app.functions.comment import comment_bp
from app.functions.chat import chat_bp
from app.functions.notice import notice_bp

from app.config import configs


def create_app(config_name=None):
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_object(configs[config_name])

    # blueprints
    app.register_blueprint(account_bp, url_prefix='/account')
    app.register_blueprint(moment_bp, url_prefix='/moment')
    app.register_blueprint(comment_bp, url_prefix='/comment')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(notice_bp, url_prefix='/notice')

    # init_extensions
    db.init_app(app)
    swagger.init_app(app)
    # mail.init_app(app)

    return app