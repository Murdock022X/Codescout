from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField
from wtforms.validators import InputRequired, Length

class SearchForm(FlaskForm):
    cluster_selections = SelectMultipleField('Clusters Filter', choices=[], validators=[InputRequired()])

    search_type = SelectMultipleField('', choices=[])

    language_filter = SelectMultipleField('Language Filter', choices=[])

    search_query = StringField('Functionality Description', validators=[Length(max=1000)])


    
