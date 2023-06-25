from flask import Blueprint, render_template, redirect, url_for, current_app, flash
from flask_login import current_user, login_required

from website.models import User, Clusters, SoftwareTypes, Organization

from werkzeug.utils import secure_filename

from website.main.forms import SearchForm, AddClusterForm, EditClusterForm

from elasticsearch import Elasticsearch

from website import db

import os

from pathlib import Path

from website.main.utils import assemble_es_url, assemble_cert_path, save_certs

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')

@login_required
@main.route('/add_cluster', methods=['GET', 'POST'])
def add_cluster(): 
    form = AddClusterForm()

    if form.validate_on_submit():
        es_host = form.es_host.data
        
        es_port = form.es_port.data

        save_certs(es_certs_file=form.es_certs_file, app=current_app, 
                   es_host=es_host, dcr_user_id=current_user.id)

        es_user = form.es_user.data

        es_password = form.es_password.data

        cluster = Clusters(es_host=es_host, es_port=es_port, es_user=es_user, 
                    es_password=es_password, user_id=current_user.id)
        
        db.session.add(cluster)

        db.session.commit()

    return render_template('add_cluster.html', form=form)

@login_required
@main.route('/search_engine', methods=['GET', 'POST'])
def search_engine():
    form = SearchForm()

    form.clusters.choices = [cluster.es_host for cluster in current_user.clusters]

    org = Organization.query.get(current_user.organization_id)

    if not org:
        flash('Please join an organization to search clusters.')
        return redirect(url_for('main.index'))

    form.software_types.choices = [sw.type for sw in org.software_types]

    form.language_filter.choices = [lang.name for lang in org.languages]

    if form.validate_on_submit():
        clusters = form.cluster_selections.data

        search_type = form.search_type.data

        search_query = form.search_query.data

    return render_template('search_engine.html', form=form)

@login_required
@main.route('/edit_cluster/<int:cluster_id>', methods=['GET', 'POST'])
def edit_cluster(cluster_id):
    cluster = Clusters.query.get(cluster_id)

    form = EditClusterForm()

    if form.validate_on_submit():
        if form.es_host.data:
            cluster.es_host = form.es_host.data
        if form.es_port.data:
            cluster.es_port = form.es_port.data
        if form.es_certs_file.data:
            save_certs(es_certs_file=form.es_certs_file, app=current_app, 
                   es_host=cluster.es_host, dcr_user_id=current_user.id)
        if form.es_user.data:
            cluster.es_user = form.es_user.data
        if form.es_password.data:
            cluster.es_password = form.es_password.data

        db.session.commit()

        return redirect(url_for('main.add_cluster'))

    return render_template('edit_cluster.html', form=form)

@login_required
@main.route('/delete_cluster/<int:cluster_id>')
def delete_cluster(cluster_id):
    cluster = Clusters.query.get(cluster_id)

    db.session.delete(cluster)

    db.session.commit()

    return redirect(url_for('main.add_cluster'))
