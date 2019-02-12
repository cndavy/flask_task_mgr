import json
import os
from functools import wraps
from urllib.request import urlopen

from flask import session, redirect, url_for, flash, request
from flask_wtf.csrf import generate_csrf, validate_csrf

from config import ALLOWED_EXTENSIONS, basedir
from models import User, app, Todo, Attatch


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
                    return redirect(url_for('login'))
            elif f.__name__=='edit':#任务更新
                if pem&Permission.ADMINISTER==Permission.ADMINISTER:
                    pass
                else:
                    flash("没有权限", 'error')
                    return redirect(url_for('login'))

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


def get_uploaddir():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])  # 拼接成合法文件夹地址
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)  # 文件夹不存在就创建
    return file_dir


class Permission:
    FOLLOW = 0X01
    COMMENT = 0X02
    WRITE_ARTICLES = 0X04
    MODERATE_COMMENTS = 0X08
    ADMINISTER = 0X80