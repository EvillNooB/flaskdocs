import phonenumbers
import arrow
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from flaskdocs.models import Groups, Staff


class AddStaffForm(FlaskForm):
    first_name = StringField('Имя',
                           validators=[DataRequired(), Length(min=2, max=35)])
    second_name = StringField('Фамилия',
                           validators=[DataRequired(), Length(min=2, max=35)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    phone = StringField('Номер телефона',
                           validators=[DataRequired()])
    group = SelectField('Группа ', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(AddStaffForm, self).__init__(*args, **kwargs)
        self.group.choices = [(group.id, group.name) for group in Groups.query.all()]


    def validate_email(self, email):
        user = Staff.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Работник с такой почтой уже зарегистрирован')

    def validate_phone(self, phone):
        try:
            input_number = phonenumbers.parse(phone.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('ErrorAfterParsing: Неправильный формат номера, убедитесь что он имеет вид +71234567890 (Без пробелов между цифрами)')
            user = Staff.query.filter_by(phone=phone.data).first()
            if user:
                raise ValidationError('Работник с таким номером уже зарегистрирован')
        except Exception as error:
            raise ValidationError(error)

class AddDocsForm(FlaskForm):
    date = StringField("Действительно до (Формат: ДД.ММ.ГГГГ)", validators=[DataRequired()])
    name = StringField("Имя документа", validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def validate_date(self, date):
        try:
            date = arrow.get(date.data,'DD.MM.YYYY')
            if date < arrow.utcnow():
                raise ValidationError("Срок действия документа истёк, невозможно добавить недействительный документ")
        except Exception as error:
            raise ValidationError(error)

class EditStaffForm(FlaskForm):
    first_name = StringField('Имя',
                           validators=[DataRequired(), Length(min=2, max=35)])
    second_name = StringField('Фамилия',
                           validators=[DataRequired(), Length(min=2, max=35)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    phone = StringField('Номер телефона',
                           validators=[DataRequired()])
    group = SelectField('Группа ', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(EditStaffForm, self).__init__(*args, **kwargs)
        self.group.choices = [(group.id, group.name) for group in Groups.query.all()]

    def validate_phone(self, phone):
        try:
            input_number = phonenumbers.parse(phone.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('ErrorAfterParsing: Неправильный формат номера, убедитесь что он имеет вид +71234567890 (Без пробелов между цифрами)')
        except Exception as error:
            raise ValidationError(error)