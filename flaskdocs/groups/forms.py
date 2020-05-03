from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from flaskdocs.models import Groups

class AddGroupForm(FlaskForm):
    name = StringField('Название группы', validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def validate_name(self, name):
        group = Groups.query.filter_by(name=name.data).first()
        if group:
            raise ValidationError('Такая группа уже существует')
        