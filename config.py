import os

DEBUG = True
SQLALCHEMY_DATABASE_URI='mysql+pymysql://flask_task:flask_task@han1/flask_task'
SQLALCHEMY_TRACK_MODIFICATIONS=True
SECRET_KEY=os.urandom(24)
#配置ORM
#app.config['SQLALCHEMY_DATABASE_URI']=
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
#CSRF加密密钥验证,字符变量由24个随机字符组成
#app.config ['SECRET_KEY']=os.urandom(24)
port=9000

UPLOAD_FOLDER = 'upload'# 设置文件上传的目标文件夹
basedir = os.path.abspath(os.path.dirname(__file__))  # 获取当前项目的绝对路径

ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'xls', 'JPG', 'PNG', 'xlsx', 'gif', 'GIF','rar','zip','doc','docx'}
#允许上传的文件后缀
SQLALCHEMY_TRACK_MODIFICATIONS = False
CSRF_ENABLED=True
WTF_CSRF_ENABLED=True