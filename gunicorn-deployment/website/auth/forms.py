from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Length

class LoginForm(FlaskForm):
    # Username 
    username = StringField('username', validators=[InputRequired(), Length(min=6, max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=50)])
    submit = SubmitField('submit')

class SignupForm(FlaskForm):
    # Username field for user account.
    username = StringField('username', validators=[InputRequired(), Length(min=6, max=50)])

    # Password field for user account.
    password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=50)])

    # First and last name field for user account.
    first_name = StringField('first_name', validators=[InputRequired(), Length(max=50)])
    last_name = StringField('last_name', validators=[InputRequired(), Length(max=50)])

    submit = SubmitField('submit')
