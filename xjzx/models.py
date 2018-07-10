from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# 类都有如下三个属性，则进行了代码封装
# 不需要继承自db.Model，因为只是代码封装，不需要对应一张表
class BaseModel(object):
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now)
    isDelete = db.Column(db.Boolean, default=False)


# 用户收藏新闻关系表
tb_news_collect = db.Table(
    'tb_news_collect',
    db.Column('user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True),
    db.Column('news_id', db.Integer, db.ForeignKey('news_info.id'), primary_key=True)
)
# 用户user_id关注作者author_id的关系表
tb_user_author = db.Table(
    'tb_user_author',
    db.Column('user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True)
)


# 新闻分类表
class NewsCategory(db.Model, BaseModel):
    __tablename__ = 'news_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    # 关系属性：新闻与分类
    # lazy='dynamic':当查询分类对象时，不会查询对应的新闻对象
    # 如果不写，默认表示：查询分类对象时，会查询出对应的新闻对象
    # 使用这个属性，可以减少与数据库查询次数
    # category=NewsCategory.query.get(1)
    # category.news==>select * from news where ....
    news = db.relationship('NewsInfo', backref='category', lazy='dynamic')


class NewsInfo(db.Model, BaseModel):
    __tablename__ = 'news_info'
    id = db.Column(db.Integer, primary_key=True)
    pic = db.Column(db.String(50))
    title = db.Column(db.String(30))
    summary = db.Column(db.String(200))
    context = db.Column(db.Text)
    source = db.Column(db.String(20), default='')
    click_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=1)
    reason = db.Column(db.String(100), default='')
    # 外键
    category_id = db.Column(db.Integer, db.ForeignKey('news_category.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    # 新闻与评论为1对多，在新闻中定义关系属性
    comments = db.relationship('NewsComment', backref='news', lazy='dynamic', order_by='NewsComment.id.desc()')
    @property
    def pic_url(self):
        return 'http://oyvzbpqij.bkt.clouddn.com/'+self.pic

class UserInfo(db.Model, BaseModel):
    __tablename__ = 'user_info'
    id = db.Column(db.Integer, primary_key=True)
    # 图片保存在磁盘上，这里存文件在磁盘的路径
    avatar = db.Column(db.String(50), default='FqpDiGx81qkUNINriHHL9TqHADho')
    nick_name = db.Column(db.String(20))
    signature = db.Column(db.String(200),default='')
    public_count = db.Column(db.Integer, default=0)
    follow_count = db.Column(db.Integer, default=0)
    mobile = db.Column(db.String(11))
    # 密码要进行加密保存
    password_hash = db.Column(db.String(200))
    gender = db.Column(db.Boolean, default=False)
    isAdmin = db.Column(db.Boolean, default=False)
    # 关系属性：新闻，一个用户可以发布多个新闻，所以定义在用户中
    news = db.relationship('NewsInfo', backref='user', lazy='dynamic')
    # 关系属性：评论，用户发布评论为一对多的关系，所以定义在用户中
    comments = db.relationship('NewsComment', backref='user', lazy='dynamic')
    # 关系属性：用户收藏新闻为多对多的关系，外键定义在第三方表，关系定义在任意类中
    news_collect = db.relationship(
        'NewsInfo',
        secondary=tb_news_collect,
        lazy='dynamic'
        # backref表示反向引用，如果不需要可以不写
    )
    # 关系属性：用户与作者的关注为多对多关系，外键定义在第三方表中，因为是自关联，关系定义在本类中
    # uesr.authors-->表示用户关注的作者
    authors = db.relationship(
        'UserInfo',
        # 外键定义在另外一张表中，需要指定关系表
        secondary=tb_user_author,
        lazy='dynamic',
        # user=UserInfo.query.get(1)
        # user.users--》表示关注这个作者user的用户
        backref=db.backref('users', lazy='dynamic'),
        # 为什么要使用primaryjoin与secondaryjoin：当前为自关联多对多，在关系表中的外键，指向的都是本表的主键
        # 表示当使用user.authors属性时，user表示用户，将user.id与关系表中的user_id匹配
        primaryjoin=id == tb_user_author.c.user_id,
        # 表示当使用user.users属性时，user表示作者，将user.id与关系表中的author_id匹配
        secondaryjoin=id == tb_user_author.c.author_id,
    )

    # user.password()==>user.password
    @property
    def password(self):
        pass

    # user.password(***)==>user.password=***，会调用如下方法
    @password.setter
    def password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def check_pwd(self, pwd):
        return check_password_hash(self.password_hash, pwd)
    @property
    def avatar_url(self):
        return 'http://oyvzbpqij.bkt.clouddn.com/' + self.avatar


class NewsComment(db.Model, BaseModel):
    __tablename__ = 'news_comment'
    id = db.Column(db.Integer, primary_key=True)
    like_count = db.Column(db.Integer, default=0)
    msg = db.Column(db.String(200))
    # 外键
    news_id = db.Column(db.Integer, db.ForeignKey('news_info.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    # 外键：自关联，回复评论的信息
    comment_id = db.Column(db.Integer, db.ForeignKey('news_comment.id'))
    # 关系属性：自关联comment.comments获取当前评论的所有回复信息
    comments = db.relationship('NewsComment', lazy='dynamic')
