from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class GoLiveForm(FlaskForm):
    stream_title = StringField('Stream Title', validators=[DataRequired()])
    submit = SubmitField('Start Stream')