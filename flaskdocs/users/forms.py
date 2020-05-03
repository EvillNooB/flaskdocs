import phonenumbers
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskdocs.models import User, Groups


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    phone = StringField('Номер телефона',
                           validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Повторите пароль',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Создать аккаунт')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Такое имя пользователя уже занято')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Такой email уже используется')

    def validate_phone(self, phone):
        try:
            input_number = phonenumbers.parse(phone.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('ErrorAfterParsing: Неправильный формат номера, убедитесь что он имеет вид +71234567890 (Без пробелов между цифрами)')
            user = User.query.filter_by(phone=phone.data).first()
            if user:
                raise ValidationError('Пользователь с таким номером уже зарегистрирован')
        except Exception as error:
            raise ValidationError(error)

class LoginForm(FlaskForm):
    login = StringField('Email или номер телефона указанный при регистрации',
                        validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить ')
    submit = SubmitField('Войти')

class UpdateAccountForm(FlaskForm):
    username = StringField('Имя пользователя',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    phone = StringField('Номер телефона',
                           validators=[DataRequired()])

    group = SelectField('Группа ', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(UpdateAccountForm, self).__init__(*args, **kwargs)
        self.group.choices = [(group.id, group.name) for group in Groups.query.all()]
        
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Такое имя пользователя уже занято')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Такой email уже используется')

    def validate_phone(self, phone):
        try:
            input_number = phonenumbers.parse(phone.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('ErrorAfterParsing: Неправильный формат номера, убедитесь что он имеет вид +71234567890 (Без пробелов между цифрами)')
            if phone.data != current_user.phone.e164:
                user = User.query.filter_by(phone=phone.data).first()
                if user:
                    raise ValidationError('Пользователь с таким номером уже зарегистрирован')
        except Exception as error:
            raise ValidationError(error)

