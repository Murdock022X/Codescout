from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, RadioField, TextAreaField, BooleanField
from website.special_fields import CheckField, MultiCheckField
from wtforms.validators import InputRequired, Length, Optional

class CreateOrgForm(FlaskForm):
    # Add organization.
    org_name = StringField('Organization Name', validators=[InputRequired(), Length(max=100)])

    submit = SubmitField('Create')

class JoinOrgForm(FlaskForm):
    # Use organization token to join org.
    org_token = StringField('Organization Enrollment Token', validators=[InputRequired(), Length(min=64, max=64)])

    submit = SubmitField('Enroll')

class AddSoftwareForm(FlaskForm):
    # Add software to clusters.
    
    # Type of software to add.
    software_type = RadioField('Software Type', validators=[InputRequired()])

    # Applicable language.
    language = RadioField('Language', validators=[InputRequired()])

    # Name for software.
    name = StringField('Name For Software', validators=[InputRequired()])

    # Should provide a good description, this will be the primary field that is searched for a match.
    description = TextAreaField('Description of Software', validators=[InputRequired()])

    # How to get the software.
    install_instructions = TextAreaField('How to Retrieve this Software', validators=[InputRequired()])

    submit = SubmitField('Add Software')

class AddSoftwareTypeForm(FlaskForm):
    # Type of software.
    type = StringField('Software Type', validators=[InputRequired()])

    submit = SubmitField('Add')

class AddLanguageForm(FlaskForm):
    # Language for software.
    lang = StringField('Language', validators=[InputRequired()])

    submit = SubmitField('Add')

class SearchForm(FlaskForm):
    # Form to search for software using Elasticsearch.

    # Software type, and language need to use 
    # dynamic choices, assign choices based on user in route.

    # Select which software type you're looking for.
    software_type = RadioField('Software Types', validators=[Optional()])

    # Select which language the software is written in.
    language = RadioField('Languages', validators=[Optional()])

    # The search query to search for.
    search_query = StringField('Functionality Description', default='', validators=[Length(max=1000)])

    submit = SubmitField('Search')
    
class AddClusterForm(FlaskForm):
    # Add a cluster to search.

    # Name of the cluster.
    name = StringField('Cluster Name', validators=[InputRequired(), Length(max=100)])

    # Elasticsearch host IP/DNS.
    es_host = StringField('Elasticsearch Host', validators=[InputRequired(), Length(max=200)])

    # Elasticsearch host port.
    es_port = StringField('Elasticsearch Port', validators=[InputRequired(), Length(max=5)])

    # Username to Elasticsearch.
    es_user = StringField('Elasticsearch Username', validators=[InputRequired()])

    # Password to Elasticsearch.
    es_password = PasswordField('Elasticsearch Password', validators=[InputRequired(), Length(min=6)])

    submit = SubmitField('Save')
