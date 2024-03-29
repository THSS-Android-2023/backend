from app.extensions.extensions import db


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="用户id")

    username = db.Column(db.String(32), unique=True, doc="账号")
    password = db.Column(db.String(256), doc="密码")
    intro = db.Column(db.String(500), doc="个性签名")
    avatar = db.Column(db.String(100), doc="头像")
    nickname = db.Column(db.String(32), doc="昵称")
    
    # email = db.Column(db.String(50), doc="邮箱")
    # mobile = db.Column(db.String(20), doc="手机号")


class Followship(db.Model):
    __tablename__ = 'followship'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="关注关系id")
    
    username_1 = db.Column(db.String(32), doc="关注者")
    username_2 = db.Column(db.String(32), doc="被关注者")


class Blackship(db.Model):
    __tablename__ = 'blackship'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="拉黑关系id")
    
    username_1 = db.Column(db.String(32), doc="拉黑者")
    username_2 = db.Column(db.String(32), doc="被拉黑者")


class Moment(db.Model):
    __tablename__ = "moment"

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="动态id")

    username = db.Column(db.String(32), doc="发布者用户名")
    title = db.Column(db.String(42), doc="TITLE")
    content = db.Column(db.String(2000), doc="Content")
    img_nums = db.Column(db.Integer, doc="图片数目")
    tag = db.Column(db.String(20), doc='信息类型，包含校园资讯、二手交易、学习科研、吃喝玩乐')
    location = db.Column(db.String(100), doc="定位")
    time = db.Column(db.DateTime, doc="创建时间")
    _type = db.Column(db.String(2), doc="类型，0-无视频，1-有视频")


class Comment(db.Model):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="评论id")
    
    moment_id = db.Column(db.Integer, doc="动态id")

    username = db.Column(db.String(32), doc="评论者用户名")
    content = db.Column(db.String(200), doc="Content")

    time = db.Column(db.DateTime, doc="创建时间")


class LikeAndStar(db.Model):
    __tablename__ = "like_and_star"

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="id")
    
    moment_id = db.Column(db.Integer, doc="动态id")
    _type = db.Column(db.Boolean, doc="type, True-Like, False-Star")
    username = db.Column(db.String(32), doc="点赞/收藏者用户名")


class Message(db.Model):
    __tablename__ = "message"

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="id")
    
    username_1 = db.Column(db.String(32), doc="发消息者")
    username_2 = db.Column(db.String(32), doc="收消息者")
    content = db.Column(db.String(200), doc="Content")

    time = db.Column(db.DateTime, doc="创建时间")


class Notice(db.Model):
    __tablename__ = "notice"

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="id")
    
    sender = db.Column(db.String(32), doc="发消息者/点赞者/回复者/被关注者")
    receiver = db.Column(db.String(32), doc="收消息者/收到点赞者/被回复者/关注者")
    content = db.Column(db.String(200), doc="消息具体内容/点赞帖子id/回复帖子id/发布帖子id")
    _type = db.Column(db.String(2), doc="类型，0-收到私信，1-信息被点赞，2-信息被回复，3-关注的用户发布新信息")
    has_noticed = db.Column(db.Boolean, doc="是否已经被提醒过")
    has_noticed_system = db.Column(db.Boolean, doc="是否已经被系统提醒过")
    first_img = db.Column(db.String(100), doc="第一张图片url")

    time = db.Column(db.DateTime, doc="创建时间")
