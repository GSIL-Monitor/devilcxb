# coding=utf-8 #-*- coding: utf-8 -*-
from flask import Flask
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin._backwards import ObsoleteAttr
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import Boolean, Table, func, or_

app = Flask(__name__)
babel = Babel(app)
app.config["BABEL_DEFAULT_LOCALE"] = "zh_hans_cn"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Aa123456@localhost/mydatabase'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    posts = db.relationship('Post', backref='post', lazy='dynamic')


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.VARCHAR(255))
    contents = db.Column(db.Text(1000))
    insert_date = db.Column(db.DateTime)


class MyModelView(ModelView):
    def __init__(self, model, session, name, endpoint, category):
        self.model = model
        self.session = session
        self.name = name
        self.endpoint = endpoint
        self.category = category

        super(MyModelView, self).__init__(model=self.model, session=self.session,
                                          name=self.name, category=self.category, endpoint=self.endpoint, url=None,
                                          static_folder=None,
                                          menu_class_name=None, menu_icon_type=None, menu_icon_value=None)

    can_create = False
    column_display_actions = False
    @property
    def can_edit(self):
        if "userQuery" == self.endpoint:
            return False
        elif "userOperation" == self.endpoint:
            return False

    @property
    def can_delete(self):
        if "userQuery" == self.endpoint:
            return False
        elif "userOperation" == self.endpoint:
            return False

    @property
    def can_export(self):
        if "userQuery" == self.endpoint:
            return True
        elif "userOperation" == self.endpoint:
            return False

    @property
    def column_list(self):
        if "userQuery" == self.endpoint or "userOperation" == self.endpoint:
            return "id", "username", "post_number"
        elif "postView" == self.endpoint:
            return "username", "title", "contents", "insert_date"
        elif "postOperation" == self.endpoint:
            return "username", "post_number", "titles"

    def get_query(self):
        if "userQuery" == self.endpoint or "userOperation" == self.endpoint:
            # print self.session.query(self.model.id.label("id"), self.model.username.label("username"), func.count(Post.id).label("post_number")).filter(self.model.id == Post.uid).group_by(Post.uid)
            return self.session.query(self.model.id.label("id"), self.model.username.label("username"), func.count(Post.id).label("post_number")).filter(self.model.id == Post.uid).group_by(Post.uid)
        elif "postView" == self.endpoint:
            # print self.session.query(User.username.label("username"), self.model.title.label("title"), self.model.contents.label("contents"), self.model.insert_date.label("insert_date")).filter(User.id == self.model.uid).order_by(self.model.insert_date.desc())
            return self.session.query(User.username.label("username"), self.model.title.label("title"), self.model.contents.label("contents"), self.model.insert_date.label("insert_date")).filter(User.id == self.model.uid).order_by(self.model.insert_date.desc())
        elif "postOperation" == self.endpoint:
            # print self.session.query(User.username.label("username"), func.count(self.model.id).label("post_number")).group_by(self.model.uid).filter(User.id == self.model.uid)
            return self.session.query(User.username.label("username"), func.count(self.model.id).label("post_number"), func.group_concat(self.model.title).label("titles")).group_by(self.model.uid).filter(User.id == self.model.uid)
        return self.session.query(self.model)

    def get_count_query(self):
        """
            Return a the count query for the model type

            A ``query(self.model).count()`` approach produces an excessive
            subquery, so ``query(func.count('*'))`` should be used instead.

            See commit ``#45a2723`` for details.
        """
        if "userQuery" == self.endpoint or "userOperation" == self.endpoint:
            return self.session.query(func.count(self.model.id)).select_from(self.model)
        elif "postOperation" == self.endpoint:
            print self.session.query(func.count(self.model.uid.distinct())).select_from(self.model)
            return self.session.query(func.count(self.model.uid.distinct())).select_from(self.model)
        return self.session.query(func.count('*')).select_from(self.model)

    @property
    def column_labels(self):
        return {"titles": u"帖子", "id": u"标示", "username": u"用户名", "post_number": u"发帖数", "insert_date": u"发帖时间"}

    @property
    def column_sortable_list(self):
        if "userQuery" == self.endpoint or "userOperation" == self.endpoint:
            return 'id', 'username'


class MyView(BaseView):
    @expose('/')
    def index(self):
        return self.render('index.html')


admin = Admin(app, name=u"测试后台")
admin.add_view(MyModelView(User, db.session, name=u'用户查询', endpoint='userQuery', category=u'用户'))
admin.add_view(MyModelView(User, db.session, name=u'用户操作', endpoint='userOperation', category=u'用户'))

admin.add_view(MyModelView(Post, db.session, name=u'帖子查看', endpoint='postView', category=u'帖子'))
admin.add_view(MyModelView(Post, db.session, name=u'帖子操作', endpoint='postOperation', category=u'帖子'))

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)
