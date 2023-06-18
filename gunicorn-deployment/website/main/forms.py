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

    es_host = StringField('Elasticsearch Host', validators=[InputRequired(), Length(max=200)])

    es_port = StringField('Elasticsearch Port')

    es_certs_file = FileField('CA Certificate', validators=[])

    es_user = StringField('Elasticsearch Username', validators=[InputRequired()])

    es_password = PasswordField('Elasticsearch Password', validators=[InputRequired(), Length(min=6)])

    submit = SubmitField('Save')

class EditClusterForm(FlaskForm):
    es_host = StringField('Elasticsearch Host', validators=[InputRequired(), Length(max=200)])

    es_port = StringField('Elasticsearch Port')

    es_certs_file = FileField('CA Certificate', validators=[])

    es_user = StringField('Elasticsearch Username', validators=[InputRequired()])

    es_password = PasswordField('Elasticsearch Password', validators=[InputRequired(), Length(min=6)])

    submit = SubmitField('Save')
