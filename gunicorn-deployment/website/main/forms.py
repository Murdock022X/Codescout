from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField
from website.special_fields import MultiCheckField
from wtforms.validators import InputRequired, Length, Optional
from website.models import Clusters
from flask_login import current_user

class AddOrgForm(FlaskForm):
    org_name = StringField('Organization Name', validators=[InputRequired(), Length(max=100)])

    submit = SubmitField('Create')

class SearchForm(FlaskForm):

    cluster_selections = MultiCheckField('Clusters Filter', choices=[])

    software_types = MultiCheckField('Software Types', choices=[])

    language_filter = MultiCheckField('Language Filter', choices=[])

    search_query = StringField('Functionality Description', validators=[Length(max=500)])

    submit = SubmitField('Search')
    
class AddClusterForm(FlaskForm):

    es_host = StringField('Elasticsearch Host', validators=[InputRequired(), Length(max=200)])

    es_port = StringField('Elasticsearch Port', validators=[InputRequired(), Length(max=5)])

    es_certs_file = FileField('CA Certificate', validators=[InputRequired()])

    es_user = StringField('Elasticsearch Username', validators=[InputRequired()])

    es_password = PasswordField('Elasticsearch Password', validators=[InputRequired(), Length(min=6)])

    submit = SubmitField('Save')

class EditClusterForm(FlaskForm):
    es_host = StringField('Elasticsearch Host', validators=[Optional(), Length(max=200)])

    es_port = StringField('Elasticsearch Port', validators=[Optional(), Length(max=5)])

    es_certs_file = FileField('CA Certificate', validators=[Optional()])

    es_user = StringField('Elasticsearch Username', validators=[Optional(), Length(max=512)])

    es_password = PasswordField('Elasticsearch Password', validators=[Optional(), Length(min=6, max=512)])

    submit = SubmitField('Save')
