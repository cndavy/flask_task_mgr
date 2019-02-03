from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, SubmitField, PasswordField, SelectField, TextAreaField, RadioField, BooleanField, \
    FileField, MultipleFileField
from wtforms.validators import DataRequired, Length, ValidationError

from config import ALLOWED_EXTENSIONS
from models import Department, User, Attatch


class LoginForm(FlaskForm):
    username=StringField(
        label="用户名",
        validators=[
            DataRequired("请输入用户名"),
            Length(5,10)
        ],
        render_kw={
            'placeholder':"请输入用户名"
        }
    )


    passwd=PasswordField(
        label="用户密码",
        validators=[
            DataRequired("请输入用户密码"),
            Length(5,10)
        ],
        render_kw={
            'placeholder':"请输入用户密码"
        }
    )
    remember_me=BooleanField(
        '记住我', default='checked',
                                validators=[DataRequired()]
         )
    submit=SubmitField(
        render_kw={
            'value':'登陆',
            'class':'btn btn-success  pull-right '
        }
    )

#任务编辑
class EditForm(FlaskForm):
 

    name=StringField(
        label='任务名称',
        validators=[
        DataRequired()
        ]
    )

    department=SelectField(
        label="所属部门",
        validators=[
            DataRequired()
        ],
        coerce = int
    )
    worker=SelectField(
        label="任务人",
        validators=[
            DataRequired()
        ],
        coerce=int
    )
    description = TextAreaField('任务备注')
    # attatches=[]
    # for attatch in Attatch.query.filter(Attatch.todo_id==todo):
    #     attatches.append(StringField(label='附件名', validators=[
    #     DataRequired()
    #     ]) )
    # upload=MultipleFileField('上传附件' ,     validators=[
    #         FileRequired(),FileAllowed(ALLOWED_EXTENSIONS, ' only!')]
    # )
    submit=SubmitField(
        render_kw={
            'value':'完成',
            'class':'btn btn-success pull-right btn-group-justified'
        }
    )

    def __init__(self,  *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        #
        # if (args is not None) and (args.__len__()==1 ):
        #     super(EditForm, self).__init__(*(), **kwargs)
        #     todo_id=args[0]
        #     for attatch in Attatch.query.filter(Attatch.todo_id == todo_id):
        #         setattr(self.__class__, "attach%s" %attatch.id, StringField("附件%s" %attatch.id,default=attatch.filepath,validators=[DataRequired()]))
        # else:
        #     super(EditForm, self).__init__(*args, **kwargs)
        self.worker.choices = [(worker.id, worker.username)
                                       for worker in User.query.order_by(User.id).all()]
        self.department.choices = [(department.id, department.name)
                               for department in Department.query.order_by(Department.id).all()]

class AttatchForm(FlaskForm):
    uploadfile=FileField(
        label='上传附件',
        validators=[
            FileRequired(),
            FileAllowed(list(ALLOWED_EXTENSIONS), '请上传合法文件:%s!'%str(ALLOWED_EXTENSIONS))],
    )

    upload_submit=SubmitField(
            render_kw={
                'value':'上传',
                'class':'btn   btn-warning  pull-right '   ,
                'role' :'button'
            }
        )

class EditProfileForm(FlaskForm):


    newpasswd = PasswordField(
        label="用户密码",
        validators=[
            DataRequired("密码长度5,10"),
            Length(5, 10)
        ],
        render_kw={
            'placeholder': "请输入用户新密码"
        }
    )
    newpasswd1 = PasswordField(
        label="用户密码",
        validators=[
            DataRequired("密码长度5,10"),
            Length(5, 10)
        ],
        render_kw={
            'placeholder': "重复输入用户新密码"
        }
    )

    submit = SubmitField('确认更改密码')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(name=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
