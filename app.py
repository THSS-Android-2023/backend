from flask import Flask
from flask_cors import CORS
from views.database import *
from views.login import login_bp


app = Flask(__name__)
app.register_blueprint(database_bp, url_prefix='/database')
app.register_blueprint(login_bp, url_prefix='/login')

app.config["SECRET_KEY"] = "secret!qwq"
CORS(app, supports_credentials=True)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# init database
db_init()

if __name__ == "__main__":
    app.run(debug=True)