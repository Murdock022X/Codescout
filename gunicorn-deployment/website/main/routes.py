from flask import Blueprint, render_template, redirect, url_for, current_app, session
from flask_login import current_user, login_required

from website.models import User, Clusters

from werkzeug.utils import secure_filename

from website.main.forms import SearchForm, AddClusterForm

from elasticsearch import Elasticsearch

from website import db

import os

from pathlib import Path

from website.main.utils import assemble_el_url

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')

@login_required
@main.route('/add_cluster', methods=['GET', 'POST'])
def addcluster():
    form = AddClusterForm()

    if form.validate_on_submit():
        el_host = form.el_host.data
        
        el_port = form.el_port.data

        cert_pth = Path(current_app.config['PROJECT_ROOT']) / Path(current_app.config['UPLOAD_FOLDER']) / Path(str(current_user.id)) / Path(str(el_host))

        cert_pth.mkdir(parents=True, exist_ok=True)

        form.el_certs_file.data.save(os.path.join(current_app.config['PROJECT_ROOT'], current_app.config['UPLOAD_FOLDER'], str(current_user.id), str(el_host), secure_filename('http_ca.crt')))

        el_user = form.el_user.data

        el_password = form.el_password.data

        cluster = Clusters(el_host=el_host, el_port=el_port, el_user=el_user, 
                    el_password=el_password, user_id=current_user.id)
        
        db.session.add(cluster)

        db.session.commit()

    return render_template('add_cluster.html', form=form)

@login_required
@main.route('/verify_el_conns')
def verify_el_conns():
    for cluster in current_user.clusters:
        cli = Elasticsearch(assemble_el_url(cluster.el_host, cluster.el_port), ca_certs=
                      os.path.join(current_app.config['PROJECT_ROOT'], 
                                   current_app.config['UPLOAD_FOLDER'], 
                                   str(current_user.id), cluster.el_host, 'http_ca.crt'), 
                                   basic_auth=
                                   (cluster.el_user, cluster.el_password))

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
@main.route()

@login_required
@main.route('/delete_cluster')
def delete_cluster():
    cluster = Clusters.query.get(session['DELETE_CLUSTER_ID'])

    db.session.delete(cluster)

    db.session.commit()
