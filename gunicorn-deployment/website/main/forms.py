from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, RadioField, TextAreaField
from website.special_fields import CheckField, MultiCheckField
from wtforms.validators import InputRequired, Length, Optional

class CreateOrgForm(FlaskForm):
    # Add organization.
    org_name = StringField('Organization Name', validators=[InputRequired(), Length(max=100)])

    submit = SubmitField('Create')

class JoinOrgForm(FlaskForm):
    org_name = StringField('Organization Name', validators=[InputRequired(), Length(max=100)])

    submit = SubmitField('Send Request')

class AddSoftwareForm(FlaskForm):
    # Add software to clusters.

    # Which clusters to add the software to.
    clusters = MultiCheckField('Elasticsearch Clusters')
    
    # Type of software to add.
    software_type = RadioField('Software Type', validators=[InputRequired()])

    # Applicable languages.
    languages = MultiCheckField('Languages')

    name = StringField('Name For Software')

    description = TextAreaField('Description of Software')

    retrieval_instructions = TextAreaField('How to Retrieve this Software')

    submit = SubmitField('Add Software')

class AddSoftwareTypeForm(FlaskForm):
    type = StringField('Software Type', validators=[InputRequired()])

    submit = SubmitField('Add')

class AddLanguageForm(FlaskForm):
    lang = StringField('Language', validators=[InputRequired()])

    submit = SubmitField('Add')

class SearchForm(FlaskForm):
    # Form to search for software using Elasticsearch.

    # Cluster selections, software types, and language filter need to use 
    # dynamic choices, assign choices based on user in route.

    # Select which clusters you want to search.
    clusters = MultiCheckField('Clusters')

    # Select which software types you're looking for.
    software_types = MultiCheckField('Software Types')

    # Select which languages the software is written in.
    languages = MultiCheckField('Languages')

    # The search query to search for.
    search_query = StringField('Functionality Description', validators=[Length(max=500)])

    submit = SubmitField('Search')
    
class AddClusterForm(FlaskForm):
    # Add a cluster to search.

    # Name of the cluster.
    name = StringField('Cluster Name', validators=[InputRequired(), Length(max=100)])

    # Elasticsearch host IP/DNS.
    es_host = StringField('Elasticsearch Host', validators=[InputRequired(), Length(max=200)])

    # Elasticsearch host port.
    es_port = StringField('Elasticsearch Port', validators=[InputRequired(), Length(max=5)])

    # Certificates for Elasticsearch.
    es_certs_file = FileField('CA Certificate', validators=[InputRequired()])

    # Username to Elasticsearch.
    es_user = StringField('Elasticsearch Username', validators=[InputRequired()])

    # Password to Elasticsearch.
    es_password = PasswordField('Elasticsearch Password', validators=[InputRequired(), Length(min=6)])

    # Should DCR use a secure connection?
    secure = RadioField('Secure Connection?', choices=['Yes', 'No'], validators=[InputRequired()])

    submit = SubmitField('Save')

class EditClusterForm(FlaskForm):
    # Edit cluster information.

    # Name of the cluster.
    name = StringField('Cluster Name', validators=[InputRequired(), Length(max=100)])

    # Elasticsearch host IP/DNS.
    es_host = StringField('Elasticsearch Host', validators=[Optional(), Length(max=200)])

    # Elasticsearch host port.
    es_port = StringField('Elasticsearch Port', validators=[Optional(), Length(max=5)])

    # Certificates for Elasticsearch.
    es_certs_file = FileField('CA Certificate', validators=[Optional()])

    # Username to Elasticsearch.
    es_user = StringField('Elasticsearch Username', validators=[Optional(), Length(max=512)])

    # Password to Elasticsearch.
    es_password = PasswordField('Elasticsearch Password', validators=[Optional(), Length(min=6, max=512)])

    submit = SubmitField('Save')
