from flask import Blueprint
admin = Blueprint('user_admin', __name__,url_prefix='/admin',
                  template_folder='templates',static_folder='static')
from . import  view