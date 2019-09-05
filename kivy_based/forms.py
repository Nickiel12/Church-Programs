from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired

class SetupStreamForm(FlaskForm):
    stream_title = StringField('Stream Title', validators=[DataRequired()])
    submit = SubmitField('Start Stream')

class GoLiveForm(FlaskForm):
    are_you_sure = BooleanField("Are you sure?")
    submit = SubmitField("Submit")