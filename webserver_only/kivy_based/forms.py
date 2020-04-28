from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired


class SetupStreamForm(FlaskForm):
    stream_title = StringField('Stream Title', validators=[DataRequired()])
    submit = SubmitField('Start Stream')


class GoLiveForm(FlaskForm):
    are_you_sure = RadioField("Are you sure?",
                              choices=[('no', 'No'),
                                       ('yes', 'Yes')], default='no')
    submit = SubmitField("Submit")
