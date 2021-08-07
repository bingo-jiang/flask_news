from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp


class RegisterForm(FlaskForm):
    mobile = StringField(
        label='手机号',
        validators=[
            DataRequired('手机号不能为空'),
            Regexp(r'^1[3456789]\d{9}$', message='格式错误'),
        ],
        render_kw={'placeholder': '请输入手机号', 'class': 'form-control'}
    )
    img_code = StringField(
        label='图片验证码',
        validators=[DataRequired('图片验证码不能为空')],
        render_kw={'placeholder': '请输入验证码', 'class': 'form-control', 'autocomplete': 'off'}
    )
    sms_code = StringField(
        label='短信验证码',
        validators=[DataRequired('验证码不能为空')],
        render_kw={'placeholder': '请输入验证码', 'class': 'form-control', 'autocomplete': 'off'}
    )
    password_hash = PasswordField(
        label='密码',
        validators=[
            DataRequired('密码不能为空'),
            Length(3, 32, '密码长度3-32')
        ],
        render_kw={'placeholder': '请输入密码', 'class': 'form-control'})
    confirm_pwd = PasswordField(
        label='确认密码',
        validators=[
            DataRequired('输入不能为空'),
            EqualTo('password_hash', '两次密码输入不一致')
        ],
        render_kw={'placeholder': '请确认密码', 'class': 'form-control'}
    )


class AuthorRegisterForm(FlaskForm):
    mobile = StringField(
        label='手机号',
        validators=[
            DataRequired('手机号不能为空'),
            Regexp(r'^1[3456789]\d{9}$', message='格式错误'),
        ],
        render_kw={'placeholder': '请输入手机号', 'class': 'form-control'}
    )
    img_code = StringField(
        label='图片验证码',
        validators=[DataRequired('图片验证码不能为空')],
        render_kw={'placeholder': '请输入验证码', 'class': 'form-control', 'autocomplete': 'off'}
    )
    sms_code = StringField(
        label='短信验证码',
        validators=[DataRequired('验证码不能为空')],
        render_kw={'placeholder': '请输入验证码', 'class': 'form-control', 'autocomplete': 'off'}
    )
    password_hash = PasswordField(
        label='密码',
        validators=[
            DataRequired('密码不能为空'),
            Length(3, 32, '密码长度3-32')
        ],
        render_kw={'placeholder': '请输入密码', 'class': 'form-control'})
    confirm_pwd = PasswordField(
        label='确认密码',
        validators=[
            DataRequired('输入不能为空'),
            EqualTo('password_hash', '两次密码输入不一致')
        ],
        render_kw={'placeholder': '请确认密码', 'class': 'form-control'}
    )


class NewsForm(FlaskForm):
    content = TextAreaField(
        label='正文',
        validators=[
            DataRequired('正文内容不能为空'),
        ],
        # render_kw={'placeholder':'请输入手机号','class':'form-control'}
    )


class NoticeForm(FlaskForm):
    title = StringField(
        label='标题',
        validators=[
            DataRequired('标题不能为空'),
        ],
        render_kw={'placeholder': '请输入标题', 'class': 'form-control'}
    )
    content = TextAreaField(
        label='正文',
        validators=[
            DataRequired('正文内容不能为空'),
        ],
        # render_kw={'placeholder': '请输入正文', 'class': 'form-control'}
    )
