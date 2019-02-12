from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from flask_wtf import CSRFProtect

import config
from datetime import datetime

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

import config

#将models绑定app
app=Flask(__name__)

app.config.from_object(config)
CSRFProtect(app)

login = LoginManager(app)


#绑定Bootstrap前端框架，可以使用框架内简洁的样式
bootstrap=Bootstrap(app)

#实例化db对象
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)


class Todo(db.Model):
    """一个关于任务的类"""
    id=db.Column(db.Integer,autoincrement=True,primary_key=True) #任务编号
    name=db.Column(db.String(50),unique=True)    #任务名称
    add_time=db.Column(db.DateTime,default=datetime.now())  #创建任务的时间
    end_time = db.Column(db.DateTime, default=None)
    description =db.Column(db.TEXT,default=None)

    status=db.Column(db.Boolean,default=False) #任务的状态
    #外键关联部门的id
    department_id=db.Column(db.Integer,db.ForeignKey('department.id'))
    worker_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    attaches = db.relationship('Attatch', backref='todo')

class Attatch(db.Model):
    '''任务附件'''
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    sourcename = db.Column(db.String(250))
    filepath=db.Column(db.String(250),unique=True)
    add_time = db.Column(db.DateTime, default=datetime.now())
    todo_id=db.Column(db.Integer,db.ForeignKey('todo.id'))
    own_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner=db.relationship('User',backref='owner')# who upload file

class Department(db.Model):
    """一个关于部门的类"""
    id=db.Column(db.Integer,autoincrement=True,primary_key=True) #任务编号
    name=db.Column(db.String(50),unique=True)
    todos=db.relationship('Todo',backref='department')
    users=db.relationship('User',backref='department')
#多对的关系表
user_role=db.Table('user_role',
                   db.Column('user_id',db.Integer,db.ForeignKey('user.id')),
                   db.Column('role_id',db.Integer,db.ForeignKey('roles.id')),
                   db.Column('addtime',db.DateTime,default=datetime.now())
                   )
class User(UserMixin,db.Model):
    """一个关于用户的类"""
    id=db.Column(db.Integer,autoincrement=True,primary_key=True) #任务编号
    username=db.Column(db.String(20), unique=True)
    pwd=db.Column(db.String(100))
    email=db.Column(db.String(50),unique=True)
    phone=db.Column(db.String(20),unique=True)
    info=db.Column(db.Text)
    add_time=db.Column(db.DateTime,default=datetime.now())
    department_id=db.Column(db.Integer,db.ForeignKey('department.id'))
    worker =db.relationship('Todo',backref='worker')#在TODO中定义worker属性
    userlog=db.relationship('Userlog',backref='user')
    role=db.relationship('Role',secondary=user_role ,backref='user')

class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    default = db.Column(db.Boolean,default=False,index=True)        #用户默认角色,default是False
    permissions = db.Column(db.Integer)                             #用户权限设置，是一个数值
   # users = db.relationship('User', backref='role',lazy='dynamic')  #和User类来进行连接


class Userlog(db.Model):
    """一个关于用户登录日志的类"""
    id=db.Column(db.Integer,autoincrement=True,primary_key=True) #任务编号
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    ip=db.Column(db.String(100))
    add_time=db.Column(db.DateTime,default=datetime.now())
    areas=db.Column(db.String(100))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

if __name__=='__main__':
    #创建数据库表
    db.create_all()
