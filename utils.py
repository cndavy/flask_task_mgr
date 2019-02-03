import json
import os
from functools import wraps
from urllib.request import urlopen

from flask import session, redirect, url_for
from config import ALLOWED_EXTENSIONS, basedir
from models import User, app


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


def get_uploaddir():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])  # 拼接成合法文件夹地址
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)  # 文件夹不存在就创建
    return file_dir