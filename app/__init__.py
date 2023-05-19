from flask import Flask
from flask_cors import CORS

from app.extensions.extensions import db, swagger

from app.functions.account import account_bp
from app.functions.moment import moment_bp

from app.config import configs


def create_app(config_name=None):
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_object(configs[config_name])

    # blueprints
    app.register_blueprint(account_bp, url_prefix='/account')
    app.register_blueprint(moment_bp, url_prefix='/moment')

    # init_extensions
    db.init_app(app)
    swagger.init_app(app)
    # mail.init_app(app)

    return app