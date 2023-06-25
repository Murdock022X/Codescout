from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, RadioField
from website.special_fields import CheckField, MultiCheckField
from wtforms.validators import InputRequired, Length, Optional

class AddOrgForm(FlaskForm):
    # Add organization.
    org_name = StringField('Organization Name', validators=[InputRequired(), Length(max=100)])

    submit = SubmitField('Create')

class AddSoftwareForm(FlaskForm):
    # Add software to clusters.

    # Which clusters to add the software to.
    clusters = MultiCheckField('Elasticsearch Clusters', validators=[InputRequired()])
    
    # Type of software to add.
    software_type = RadioField('Software Type', validators=[InputRequired()])

    # Applicable languages.
    languages = MultiCheckField('Languages', validators=[Optional()])

    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    # Form to search for software using Elasticsearch.

    # Cluster selections, software types, and language filter need to use 
    # dynamic choices, assign choices based on user in route.

    # Select which clusters you want to search.
    clusters = MultiCheckField('Clusters Filter')

    # Select which software types you're looking for.
    software_types = MultiCheckField('Software Types')

    # Select which languages the software is written in.
    language_filter = MultiCheckField('Language Filter')

    # The search query to search for.
    search_query = StringField('Functionality Description', validators=[Length(max=500)])

    submit = SubmitField('Search')
    
class AddClusterForm(FlaskForm):
    # Add a cluster to search.

    # Elasticsearch host IP/DNS.
    es_host = StringField('Elasticsearch Host', validators=[InputRequired(), Length(max=200)])

    # Elasticsearch host port.
    es_port = StringField('Elasticsearch Port', validators=[InputRequired(), Length(max=5)])

    # Certificate file to verify 
    es_certs_file = FileField('CA Certificate', validators=[InputRequired()])

    # Elasticsearch username.
    es_user = StringField('Elasticsearch Username', validators=[InputRequired()])

    # Password to Elasticsearch.
    es_password = PasswordField('Elasticsearch Password', validators=[InputRequired(), Length(min=6)])

    submit = SubmitField('Save')

class EditClusterForm(FlaskForm):
    # Edit cluster information.


    es_host = StringField('Elasticsearch Host', validators=[Optional(), Length(max=200)])

    # Edi
    es_port = StringField('Elasticsearch Port', validators=[Optional(), Length(max=5)])

    es_certs_file = FileField('CA Certificate', validators=[Optional()])

    es_user = StringField('Elasticsearch Username', validators=[Optional(), Length(max=512)])

    es_password = PasswordField('Elasticsearch Password', validators=[Optional(), Length(min=6, max=512)])

    submit = SubmitField('Save')
