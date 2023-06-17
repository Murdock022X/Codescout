from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, SubmitField, PasswordField, FileField
from wtforms.validators import InputRequired, Length

class SearchForm(FlaskForm):
    cluster_selections = SelectMultipleField('Clusters Filter', choices=[], validators=[InputRequired()])

    search_type = SelectMultipleField('Software Type', choices=[])

    language_filter = SelectMultipleField('Language Filter', choices=[])

    search_query = StringField('Functionality Description', validators=[InputRequired(), Length(max=500)])

    submit = SubmitField('Search')
    
class AddClusterForm(FlaskForm):

    el_host = StringField('Elasticsearch Host', validators=[InputRequired(), Length(max=200)])

    el_port = StringField('Elasticsearch Port')

    el_certs_file = FileField('CA Certificate', validators=[])

    el_user = StringField('Elasticsearch Username', validators=[InputRequired()])

    el_password = PasswordField('Elasticsearch Password', validators=[InputRequired(), Length(min=6)])

    submit = SubmitField('Save')
