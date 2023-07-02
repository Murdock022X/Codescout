from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Length, Optional


class LoginForm(FlaskForm):
    # Username 
    username = StringField('Username', validators=[InputRequired(), Length(min=6, max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=50)])
    submit = SubmitField('Submit')

class SignupForm(FlaskForm):
    # Username field for user account.
    username = StringField('Username', validators=[InputRequired(), Length(min=6, max=50)])

    # Password field for user account.
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=50)])

    # First and last name field for user account.
    first_name = StringField('First Name', validators=[InputRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[InputRequired(), Length(max=50)])

    submit = SubmitField('Submit')
