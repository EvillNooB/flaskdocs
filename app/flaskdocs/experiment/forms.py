from flask_wtf import FlaskForm
from wtforms.fields import html5 as h5fields
from wtforms.widgets import html5 as h5widgets
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Email, ValidationError
import arrow

class AddProductForm(FlaskForm):
    product_name = StringField("Наименование", validators=[DataRequired()])
    vendor = StringField("Производитель", validators=[DataRequired()])
    manufactured_date = StringField("Произведено в (Формат: ДД.ММ.ГГГГ)", validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def validate_date(self, manufactured_date):
        try:
            date = arrow.get(manufactured_date.data, 'DD.MM.YYYY')
        except Exception as error:
            raise ValidationError(error)    