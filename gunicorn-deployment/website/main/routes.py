from flask import render_template, Blueprint, redirect, url_for, current_app, flash, get_flashed_messages, session
from flask_login import current_user, login_required

from website.models import Users, Clusters, SoftwareTypes, Organizations

from werkzeug.utils import secure_filename

from website.main.forms import CreateOrgForm, JoinOrgForm, SearchForm, AddClusterForm, EditClusterForm, AddSoftwareForm

from elasticsearch import Elasticsearch

from website import db

import os

from pathlib import Path

from website.main.utils import assemble_es_url, assemble_cert_path, save_certs, get_es_connection, org_required

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    return render_template('index.html', org=org)

@main.route('/join_organization', methods=['GET', 'POST'])
@login_required
def join_organization():
    form = JoinOrgForm()

    if form.validate_on_submit():
        org = Organizations(name=form.org_name.data)

        current_user.organization_id = org.id

        db.session.commit()

    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    return render_template('join_org.html', form=form, org=org)

@main.route('/create_organization', methods=['GET', 'POST'])
@login_required
def create_organization():
    form = CreateOrgForm()

    if form.validate_on_submit():
        org = Organizations(name=form.org_name.data)

        db.session.add(org)
        db.session.commit()
        current_user.organization_id = org.id
        current_user.organization_name = org.name

        db.session.commit()

    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    return render_template('add_org.html', form=form, org=org)

@main.route('/search_engine', methods=['GET', 'POST'])
@login_required
@org_required
def search_engine():
    
    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)
    
    if not org:
        flash('Please join an organization to search clusters.', category='danger')
        return redirect(url_for('main.index'))

    form = SearchForm()

    form.clusters.choices = [(cluster.name + ' ({}:{})'.format(cluster.es_host, cluster.es_port), cluster.id) for cluster in org.clusters]

    form.software_types.choices = [sw.type for sw in org.software_types]

    form.languages.choices = [lang.name for lang in org.languages]

    if form.validate_on_submit():
        clusters = form.cluster_selections.data

        search_type = form.search_type.data

        search_query = form.search_query.data

    return render_template('search_engine.html', form=form, org=org)

@main.route('/add_software')
@login_required
@org_required
def add_software():
    form = AddSoftwareForm()

    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    form.clusters.choices = [(cluster.name + ' ({}:{})'.format(cluster.es_host, cluster.es_port), cluster.id) for cluster in org.clusters]

    form.software_type.choices = [software_type.type for software_type in org.software_types]

    form.languages.choices = [lang.name for lang in org.languages]

    if form.validate_on_submit():
        
        for cluster_id in form.clusters.data:
            cluster = Clusters.query.get(cluster_id)

            es = get_es_connection(host=cluster.es_host,
                                   port=cluster.es_port,
                                   secure=cluster.secure,
                                   org_name=org,
                                   username=cluster.username,
                                   password=cluster.password,
                                   app=current_app)
            
            es.index(index='software-index', )

    return render_template('add_software.html', form=form, org=org)

@main.route('/test_es_conn/<int:cluster_id>')
@login_required
@org_required
def test_es_conn(cluster_id):
    cluster = Clusters.query.get(cluster_id)

    org = Organizations.query.get(current_user.organization_id)

    es = get_es_connection(host=cluster.es_host, 
                             port=cluster.es_port, 
                             secure=cluster.secure, 
                             org_name=org.name,
                             username=cluster.es_user, 
                             password=cluster.es_password,
                             app=current_app)
    
    

    return True

@main.route('/clusters', methods=['GET', 'POST'])
@login_required
@org_required
def clusters(): 
    form = AddClusterForm()

    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    if form.validate_on_submit():
        name = form.name.data

        es_host = form.es_host.data
        
        es_port = form.es_port.data

        es_user = form.es_user.data

        es_password = form.es_password.data

        secure = form.secure.data
        sb = True
        if secure == 'No':
            sb = False

        cluster = Clusters(name=name, es_host=es_host, es_port=es_port, es_user=es_user, 
                    es_password=es_password, secure=sb, organization_id=org.id)
        
        db.session.add(cluster)

        db.session.commit()

        save_certs(certs_file=form.es_certs_file, app=current_app, 
                   host=es_host, org_name=org.name)

    return render_template('clusters.html', form=form, org=org)

@main.route('/edit_cluster/<int:cluster_id>', methods=['GET', 'POST'])
@login_required
@org_required
def edit_cluster(cluster_id):
    """
    + Completed +
    Edit cluster information.

    :param cluster_id: The id of the cluster to edit.
    :return: If form had a valid POST return redirect to the add cluster page. 
    Else render the template for add cluster.
    """

    # Get the cluster to be edited.
    cluster = Clusters.query.get(cluster_id)

    # Get the form for editing.
    form = EditClusterForm()

    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    # Validate the form submission.
    if form.validate_on_submit():
        # Edit the name data.
        if form.name.data:
            cluster.name = form.name.data

        # Edit the host data.
        if form.es_host.data:
            cluster.es_host = form.es_host.data

        # Edit the port data.
        if form.es_port.data:
            cluster.es_port = form.es_port.data

        # Edit the cert file.
        if form.es_certs_file.data:
            save_certs(certs_file=form.es_certs_file, app=current_app, 
                   host=cluster.es_host, org_name=Organizations.query.get(current_user.organization_id).name)
        
        # Edit the Elasticsearch user.
        if form.es_user.data:
            cluster.es_user = form.es_user.data
        
        # Edit the Elasticsearch password.
        if form.es_password.data:
            cluster.es_password = form.es_password.data

        # Commit the edits.
        db.session.commit()

        # Redirect to add cluster page.
        return redirect(url_for('main.clusters'))

    # Render the editing template.
    return render_template('edit_cluster.html', form=form, org=org)

@main.route('/delete_cluster/<int:cluster_id>')
@login_required
@org_required
def delete_cluster(cluster_id):
    """
    + Completed +
    Route to delete a cluster from the database.

    :param cluster_id: Id of the cluster to delete.
    :return: Redirect to the add cluster web page.
    """

    # Get the cluster.
    cluster = Clusters.query.get(cluster_id)

    # Delete the cluster from the database.
    db.session.delete(cluster)

    # Save deletion.
    db.session.commit()

    # Redirect to the add cluster page.
    return redirect(url_for('main.clusters'))

@main.route('/setup_elastic/<int:cluster_id>')
@login_required
@org_required
def setup_elastic(cluster_id: int):
    cluster = Clusters.query.get(cluster_id)
    
    org = Organizations.query.get(current_user.organization_id)

    es = get_es_connection(host=cluster.es_host, 
                            port=cluster.es_port, 
                            secure=cluster.secure, 
                            org_name=org.name,
                            username=cluster.es_user, 
                            password=cluster.es_password,
                            app=current_app)
    
    es.indices.create(index='software-index')

    return redirect(url_for('main.clusters'))
