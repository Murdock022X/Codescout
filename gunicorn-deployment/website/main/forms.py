from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Length

class SearchForm(FlaskForm):
    cluster_selections = SelectMultipleField('Clusters Filter', choices=[], validators=[InputRequired()])

    search_type = SelectMultipleField('Software Type', choices=[])

    language_filter = SelectMultipleField('Language Filter', choices=[])

    search_query = StringField('Functionality Description', validators=[Length(max=1000)])

    submit = SubmitField('Search')
    
class AccountSettingsForm(FlaskForm):
    cluster

    password = PasswordField('Old ', validators=[InputRequired(), Length(min=6, max=50)])

    submit = SubmitField('Save')
