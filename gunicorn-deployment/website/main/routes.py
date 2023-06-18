from flask import Blueprint, render_template, redirect, url_for, current_app, session
from flask_login import current_user, login_required

from website.models import User, Clusters

from werkzeug.utils import secure_filename

from website.main.forms import SearchForm, AddClusterForm, EditClusterForm

from elasticsearch import Elasticsearch

from website import db

import os

from pathlib import Path

from website.main.utils import assemble_es_url

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

        cert_pth = Path(current_app.config['PROJECT_ROOT']) / Path(current_app.config['UPLOAD_FOLDER']) / Path(str(current_user.id)) / Path(str(es_host))

        cert_pth.mkdir(parents=True, exist_ok=True)

        form.el_certs_file.data.save(str(cert_pth / Path(secure_filename('http_ca.crt'))))

        es_user = form.es_user.data

        es_password = form.es_password.data

        cluster = Clusters(es_host=es_host, es_port=es_port, es_user=es_user, 
                    es_password=es_password, user_id=current_user.id)
        
        db.session.add(cluster)

        db.session.commit()

    return render_template('add_cluster.html', form=form)

@login_required
@main.route('/verify_el_conns')
def verify_el_conns():
    for cluster in current_user.clusters:
        cli = Elasticsearch(assemble_es_url(cluster.es_host, cluster.es_port), ca_certs=
                      os.path.join(current_app.config['PROJECT_ROOT'], 
                                   current_app.config['UPLOAD_FOLDER'], 
                                   str(current_user.id), cluster.es_host, 'http_ca.crt'), 
                                   basic_auth=
                                   (cluster.es_user, cluster.es_password))

    return redirect(url_for('main.index'))

@login_required
@main.route('/search_engine', methods=['GET', 'POST'])
def search_engine():
    form = SearchForm()

    if form.validate_on_submit():
        clusters = form.cluster_selections.data

        search_type = form.search_type.data

        search_query = form.search_query.data

    return render_template('search_engine.html', form=form)

@login_required
@main.route('/edit_cluster/<int:cluster_id>')
def edit_cluster(cluster_id):
    cluster = Clusters.query.get(cluster_id)

    form = EditClusterForm()

    if form.validate_on_submit():
        pass

    return render_template('edit_cluster.html')

@login_required
@main.route('/delete_cluster/<int:cluster_id>')
def delete_cluster(cluster_id):
    cluster = Clusters.query.get(cluster_id)

    db.session.delete(cluster)

    db.session.commit()

    return redirect(url_for('main.add_cluster'))
