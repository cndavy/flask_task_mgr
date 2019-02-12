import os
import random
from datetime import datetime, time

import flask
from flask import render_template, redirect, request, url_for, flash, session, g, jsonify, send_from_directory, Flask
from flask_bootstrap import Bootstrap
from flask_login import current_user, login_user, logout_user
from flask_wtf import csrf
from flask_wtf.csrf import generate_csrf
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from config import basedir, UPLOAD_FOLDER
from forms import EditForm, EditProfileForm, LoginForm, AttatchForm
from models import app, Userlog, User, Todo, db, Attatch
from utils import getPermisson, islogin, allowed_file, get_uploaddir, havePermission, Permission


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500



@app.before_request
def before_request():
    if not 'user' in session:
        g.islogin = False
    else :
        g.islogin =True

@app.after_request
def after_request(response):
    # 调用函数生成 csrf_token
    csrf_token = generate_csrf()
    # 通过 cookie 将值传给前端
    response.set_cookie("csrf_token", csrf_token)
    return response


#首页
@app.route('/')
@islogin
def index():
    return render_template('base.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        pwd = form.passwd.data
        if user is None or not check_password_hash(user.pwd,pwd):
            flash('用户名或密码错误', 'error')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        #time.sleep(2)
        flash('登陆成功', 'ok')
        #session['user'] = user.name
        session['roles'] = '[%s]' % ','.join([role.name for role in user.role])
        return redirect(url_for('list',page=1))

    return render_template('login.html', title='登录', forms=form)

#任务列表
@app.route('/list/<int:page>',methods=['GET','POST'])
@app.route('/list/')
@islogin
def list(page=1):
    forms = EditForm(csrf_enabled=True)
    if forms.validate_on_submit():
        add()
    todos = Todo.query.order_by(Todo.status).order_by(Todo.add_time.desc()).paginate(page,per_page=6)
    users = User.query.all()
    return render_template('list.html',todos=todos,users=users,roles=session['roles'],forms=forms)


#点击完成
@app.route('/todoup/<int:page>/<int:id>')
@app.route('/todoup/')
@islogin
def todoup(page,id):
    todo=Todo.query.filter_by(id=id).first()
    permission = getPermisson()

    if permission  & Permission.ADMINISTER:
            pass
    todo.status=1
    todo.end_time = datetime.now()
    db.session.add(todo)
    userlog=Userlog(
        user_id=session['user_id'],

    )
    db.session.add(userlog)

    db.session.commit()
    return redirect(url_for('list',page=page))


#点击未完成
@app.route('/tododown/<int:page>/<int:id>')
@app.route('/tododown/')
@islogin
def tododown(page,id):
    todo=Todo.query.filter_by(id=id).first()
    todo.status=0

    db.session.add(todo)
    db.session.commit()
    return redirect(url_for('list',page=page))


#删除操作
@app.route('/delete/<int:page>/<int:id>')
@islogin
@havePermission
def delete(page,id):
    todo=Todo.query.filter_by(id=id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('list',page=page))


#编辑操作
@app.route('/edit/<int:page>/<int:id>',methods=['GET','POST'])
@islogin
@havePermission
def edit(page,id):
    forms=EditForm()
    todo = Todo.query.filter_by(id=id).first()
    attatches = Attatch.query.filter(Attatch.todo_id==id)
    oldname = todo.name
    oldpart=todo.department_id
    oldwork_id=todo.worker_id
    olddescription=todo.description
    if request.method == 'POST':
        todo.name=forms.name.data
        todo.worker_id=forms.worker.data
        todo.department_id=forms.department.data
        todo.description=forms.description.data
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('list', page=page))
    forms.name.data=oldname
    forms.department.data=oldpart
    forms.worker.data = oldwork_id
    forms.description.data=olddescription
    forms.attatches=attatches
    forms.todo_id=id
    forms.page=page
    return render_template('edit.html',forms=forms)

#Search
@app.route('/search/',methods=['GET','POST'])
@islogin
def search():
    str=request.form['searchstr']
    todos = Todo.query.filter(Todo.name.like("%%%s%%" % str)).paginate(1,per_page=4)
    workers = User.query.all()
    return render_template('list.html', todos=todos, users=workers)



#添加任务
@app.route('/add/',methods=['POST'])
@islogin

def add():
    todoname=request.form['name']
    worker=request.form['worker']
    todo=Todo(name=todoname,worker_id=worker)
    if (Todo.query.filter_by(name=todoname).first()):
        flash("此任务已经存在！",'ok')
    else:
        db.session.add(todo)
        db.session.commit()
        flash("任务添加完成！")
    return redirect(url_for('list'))

#用户注销
@app.route('/logout')
@islogin
def logout():
    session.pop('user',None)
    logout_user()
    return redirect(url_for('login'))

#用户注销
@app.route('/backhead/')
@islogin
def backhead():

    return redirect(url_for('index'))

@app.route('/edit_profile', methods=['GET', 'POST'])
@islogin

def edit_profile():
    form = EditProfileForm(current_user.username,csrf_enabled=True)
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        newpasswd = form.newpasswd.data
        newpasswd1 = form.newpasswd1.data
        if newpasswd!=newpasswd1 :
            flash('用户名或密码错误', 'error')
            return redirect(url_for('edit_profile'))
        user.pwd=generate_password_hash(newpasswd)
        db.session.add(user)
        db.session.commit()
    return render_template("edit_profile.html",forms=form)


@app.route('/upload_delete/<int:att_id>/<int:todo_id>/<int:page>' )
@islogin
@havePermission
def upload_delete(att_id,todo_id,page):
    att=Attatch.query.filter(Attatch.id==att_id,Attatch.todo_id==todo_id).first()
    filename=get_uploaddir()+os.path.sep+att.filepath
    try:
        if os.path.isfile(filename):
            os.remove(filename)
            db.session.delete(att)
            db.session.commit()
            flash('删除附件成功！','ok')
        else:
            flash("附件%s文件没有找到！"%filename,'error')

    except:
        flash("删除附件%s出错！"%filename,'error')

    return redirect(url_for('edit',page=page,id=todo_id))

@app.route('/uploadlist/<int:todo_id>')
@islogin
def uploadlist(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    return render_template("uploadlist.html",forms=todo)
    pass

@app.route('/download/<int:att_id>')
@islogin
@havePermission
def download(att_id):
    if request.method=="GET":
        att = Attatch.query.filter(Attatch.id == att_id).first()
        filename = get_uploaddir() + os.path.sep + att.filepath
        if os.path.isfile(filename):
            return send_from_directory(UPLOAD_FOLDER,att.filepath,as_attachment=True)
        os.abort(404)

@app.route('/upload/<int:todo_id>/<int:page>',methods=['GET', 'POST'])
@islogin
def upload(todo_id,page):
    forms=AttatchForm(csrf_enabled=True)
    forms.page=page
    forms.todo_id=todo_id
    attatches = Attatch.query.filter(Attatch.todo_id == todo_id).all()
    forms.attatches=attatches

    if  forms.validate_on_submit():
        file_dir = get_uploaddir()
        f = request.files['uploadfile']  # 从表单的file字段获取文件，myfile为该表单的name值
        if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
            fname = f.filename
            ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
            #unix_time = int(time.time())
            fn = datetime.now().strftime('%Y%m%d%H%M%S')
            fn = fn + '_%d' % random.randint(0, 100)
            new_filename = fn+ '.' + ext  # 修改文件名
            f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录
            att=Attatch()
            att.sourcename=secure_filename(fname)
            att.todo_id=todo_id
            att.own_id=session.get('user_id')
            att.filepath=new_filename
            db.session.add(att)
            db.session.commit()
            flash("上传附件成功",'ok')
            return redirect(url_for('edit',page=page,id=todo_id))
        else:
            flash("上传失败", 'error')
            return redirect(url_for('edit', page=page, id=todo_id))
    else :
        return render_template('upload.html',forms=forms)



if __name__ == '__main__':
    app.run(port='9000')
