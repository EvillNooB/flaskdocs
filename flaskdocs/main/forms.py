from flask_wtf import FlaskForm
from wtforms.fields import html5 as h5fields
from wtforms.widgets import html5 as h5widgets
from wtforms import SubmitField

class NotificationSettingsForm(FlaskForm):
    first = h5fields.IntegerField("Первое уведомление когда остается дней", widget=h5widgets.NumberInput(min=1, step=1))
    second = h5fields.IntegerField('Второе уведомление когда остается дней', widget=h5widgets.NumberInput(min=1, step=1))
    third = h5fields.IntegerField('Третье уведомление когда остается дней',
                                  widget=h5widgets.NumberInput(min=1, step=1))
    submit = SubmitField('Сохранить')