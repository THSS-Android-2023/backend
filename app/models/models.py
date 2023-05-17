from app.extensions.extensions import db


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="用户id")

    username = db.Column(db.String(32), unique=True, doc="账号")
    password = db.Column(db.String(256), doc="密码")
    intro = db.Column(db.String(500), doc="个性签名")
    avatar = db.Column(db.String(400000), doc="头像")
    nickname = db.Column(db.String(32), doc="昵称")
    
    # email = db.Column(db.String(50), doc="邮箱")
    # mobile = db.Column(db.String(20), doc="手机号")


class Followship(db.Model):
    __tablename__ = 'followship'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="关系id")
    
    username_1 = db.Column(db.String(32), doc="关注者")
    username_2 = db.Column(db.String(32), doc="被关注者")
