import json
from functools import wraps
from urllib.request import urlopen

from flask import session, redirect, url_for, flash, request
from flask_wtf.csrf import generate_csrf, validate_csrf

from config import ALLOWED_EXTENSIONS
from models import User, Attatch, Todo


def getPermisson():
    user_id = session['user_id']
    user = User.query.filter_by(id=user_id).first()
    roles = user.role
    permission = 0
    for role in roles:
        permission += role.permissions
    return permission


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_ip_area(ip):
    url='http://ip.taobao.com/service/getIpInfo.php?ip=%s' %(ip)
    json_data=urlopen(url).read().decode('utf-8')
    s_data=json.loads(json_data)
    country=s_data['data']['country']
    if country=='xx':
        country==''
    city=s_data['data']['city']
    if city=='xx':
        city==''
    return country+city


def islogin(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        if not 'user_id' in session:
            return redirect(url_for('login'))
        return f(*args,**kwargs)
    return wrapper

def havePermission(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        if not 'user_id' in session:
            return redirect(url_for('login'))
        else:
            pem=getPermisson()
            c = request.cookies.get('csrf_token')
            s = session.get('csrf_token')
            try:
                validate_csrf(c)
            except:
                return redirect(url_for('login'))
                pass
            if f.__name__=='delete':#任务删除
                #Todo.query.filter_by(id=kwargs.get('id'))
                if pem&Permission.ADMINISTER==Permission.ADMINISTER:
                    pass
                else:
                    flash("没有权限", 'error')
                    return redirect(url_for('list'))
            elif f.__name__=='edit':#任务更新
                if pem&Permission.ADMINISTER==Permission.ADMINISTER:
                    pass
                else:

                    flash("没有权限", 'error')
                    return redirect(url_for('list'))
            elif f.__name__=='todoup' or f.__name__=='tododown':# 完成
                if pem&Permission.ADMINISTER==Permission.ADMINISTER:
                    pass
                else:
                    todo = Todo.query.filter(Todo.id == kwargs.get('id')
                                               ).first()
                    if str(todo.worker_id) == session['user_id']:  # 任务被分派人
                        pass
                    else:
                        flash("没有权限", 'error')
                        return redirect(url_for('list'))


            elif f.__name__=='upload_delete':#附件删除


                if pem & Permission.ADMINISTER == Permission.ADMINISTER:
                    pass
                else:
                    flash("没有权限附件删除", 'error')
                    return redirect(url_for('login'))
            elif f.__name__=='download': #下载附件
                if pem & Permission.ADMINISTER == Permission.ADMINISTER:
                    pass
                else:
                    att = Attatch.query.filter(Attatch.id == kwargs.get('att_id')
                                               ).first()
                    if str(att.own_id) == session['user_id']:  # 任务被分派人
                        pass
                    else:
                        flash("没有权限下载附件", 'error')
                        return redirect(url_for('login'))
            else:
                pass


            return f(*args,**kwargs)
    return wrapper


class Permission:
    FOLLOW = 0X01
    COMMENT = 0X02
    WRITE_ARTICLES = 0X04
    MODERATE_COMMENTS = 0X08
    ADMINISTER = 0X80


def create_csrf_token(response):
    # 调用函数生成 csrf_token
    csrf_token = generate_csrf()
    # 通过 cookie 将值传给前端
    response.set_cookie("csrf_token", csrf_token)
    return response

from flask import g
def set_var_g():
    if not 'user_id' in session:

        g.islogin = False
    else:
        g.islogin = True
        g.isadmin = (getPermisson() & Permission.ADMINISTER) > 0