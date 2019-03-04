import time
from flask import render_template, request, json

from models import Todo
from utils import create_csrf_token, set_var_g
from . import admin


@admin.before_request
def before_request():
    set_var_g()


@admin.after_request
def after_request(response):
    return create_csrf_token(response)


@admin.route('/test')
def hello():
    return 'hello world!'

@admin.route('/list')
def list():
     return render_template('admin/task_list.html',title='任务列表')
@admin.route('json/task_list')
def task_list(*args,**kwargs):
    from models import User
    print (request.args)
    search=request.args['search']
    if search=='':
        search='%'
    order = request.args['order']
    offset = request.args['offset']
    limit = request.args['limit']
    count=0
    count = len(Todo.query.filter(Todo.name.like("%%%s%%" % search)).all())
    if 'sort' in request.args:
        sort = request.args['sort']
        todos = Todo.query.filter(Todo.name.like("%%%s%%" % search)).order_by('%s  %s'%(sort ,order)).offset(offset).limit(limit).all()

    else:
        todos = Todo.query.filter(Todo.name.like("%%%s%%" % search)).order_by('%s  %s '%('id' ,order)).offset(offset).limit(limit).all()
    #table_todo=Todo.metadata.tables['todo']
    cc=[('name','任务名称'),('status','任务状态'),('add_time','安排开始时间'),('end_time','任务完成时间')]
    jsondict={}
    jsondict['total']=count
    jsondict['rows']=[{
        'id':i.id,
        'name':i.name,
        'status':i.status,
        'add_time':i.add_time.strftime("%Y-%m-%d %H:%M:%S"),
        'end_time':i.end_time.strftime("%Y-%m-%d %H:%M:%S")} for i in todos]
    result =json.dumps(jsondict)

    return  result
   # return render_template('list.html',title='人员列表',users=users)