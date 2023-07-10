from flask import render_template, Blueprint, redirect, url_for, current_app, flash, get_flashed_messages, session
from flask_login import current_user, login_required

from website.models import Users, Clusters, SoftwareTypes, Languages, Organizations, Messages

from werkzeug.utils import secure_filename

from website.main.forms import CreateOrgForm, JoinOrgForm, SearchForm, \
AddClusterForm, EditClusterForm, AddSoftwareForm, AddSoftwareTypeForm, \
AddLanguageForm, MessageForm

from website import db

from website.main.decorators import org_required, admin_required
from website.main.utils import save_certs, get_es_connection, get_search_page_data, PageData

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    return render_template('index.html', org=org)

@main.route('/inbox')
@login_required
@org_required
def inbox():

    org = Organizations.query.get(current_user.organization_id)
    
    return render_template('inbox.html', org=org, messages=current_user.messages)

@main.route('/create_message')
@login_required
@org_required
@admin_required
def create_message():

    org = Organizations.query.get(current_user.organization_id)

    form = MessageForm()

    if form.validate_on_submit():
        message = Messages(title=form.title.data, 
                           message=form.message.data, 
                           user_id=current_user.id)
        
        db.session.add(message)
        db.session.commit()

    return render_template('create_message.html', org=org, form=form)

@main.route('/message_view/<int:message_id>')
@login_required
@org_required
def message_view(message_id) -> str:
    """A Flask route for the DCR website that allows the user to view a specific message.

    Args:
        message_id (int): The database id for the message.

    Returns:
        str: The rendered html string for the message view.
    """

    org = Organizations.query.get(current_user.organization_id)

    message = Messages.query.get(message_id)

    return render_template('message_view.html', org=org, message=message)

@main.route('/cluster_requests')
@login_required
@org_required
def cluster_requests():
    return render_template()

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
        current_user.admin_status = True

        db.session.commit()

    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    return render_template('add_org.html', form=form, org=org)

@main.route('/search_engine/<int:page_idx>', methods=['GET', 'POST'])
@login_required
@org_required
def search_engine(page_idx):

    org = Organizations.query.get(current_user.organization_id)

    form = SearchForm()

    form.clusters.choices = [(cluster.id, cluster.name + ' ({}:{})'.format(cluster.es_host, cluster.es_port)) for cluster in org.clusters]

    form.software_type.choices = [sw.type for sw in org.software_types]

    form.languages.choices = [lang.name for lang in org.languages]

    hit_responses = []
    hit_total = 0

    if form.validate_on_submit():
        clusters = form.clusters.data

        software_type = form.software_type.data

        search_query = form.search_query.data

        for cluster_id in clusters:
            cluster = Clusters.query.get(cluster_id)
            es = get_es_connection(host=cluster.es_host,
                                    port=cluster.es_port,
                                    secure=cluster.secure,
                                    org_name=org.name,
                                    username=cluster.es_user,
                                    password=cluster.es_password,
                                    app=current_app)
            
            response = es.search(index='software-index', query={"match": {"description": {"query": search_query}}})

            for resp in response['hits']['hits']:
                hit_responses.append(PageData(resp, cluster.id))

            hit_total += response['hits']['total']['value']

    else:

        for cluster in org.clusters:
            es = get_es_connection(host=cluster.es_host,
                                    port=cluster.es_port,
                                    secure=cluster.secure,
                                    org_name=org.name,
                                    username=cluster.es_user,
                                    password=cluster.es_password,
                                    app=current_app)
            
            response = es.search(index="software-index", query={"match_all": {}})

            for resp in response['hits']['hits']:
                hit_responses.append(PageData(resp, cluster.id))

            hit_total += response['hits']['total']['value']

    total_pages = hit_total // current_app.config["SEARCH_PAGE_LEN"]

    if hit_total % current_app.config["SEARCH_PAGE_LEN"] > 0:
        total_pages += 1

    page_len = current_app.config["SEARCH_PAGE_LEN"]
    if page_idx == total_pages - 1:
        page_len = hit_total % current_app.config["SEARCH_PAGE_LEN"]

    page_data = get_search_page_data(data=hit_responses, 
                                     page_idx=page_idx, 
                                     page_len=current_app.config["SEARCH_PAGE_LEN"])

    return render_template('search_engine.html', form=form, org=org, hit_total=hit_total, total_pages=total_pages, page_data=page_data, page_idx=page_idx, page_len=page_len)

@main.route('/software_info/<es_id>/<int:cluster_id>')
@login_required
@org_required
def software_info(es_id, cluster_id):

    org = Organizations.query.get(current_user.organization_id)

    cluster = Clusters.query.get(cluster_id)

    es = get_es_connection(host=cluster.es_host,
                                    port=cluster.es_port,
                                    secure=cluster.secure,
                                    org_name=org.name,
                                    username=cluster.es_user,
                                    password=cluster.es_password,
                                    app=current_app)

    response = es.search(index='software-index', query={"term": {"_id": es_id}})

    item = response['hits']['hits'][0]['_source']

    return render_template('software_info.html', org=org, item=item)

@main.route('/add_software_type', methods=['GET', 'POST'])
@login_required
@org_required
def add_software_type():
    form = AddSoftwareTypeForm()

    org = Organizations.query.get(current_user.organization_id)

    if form.validate_on_submit():
        type = form.type.data

        for swt in org.software_types:
            if swt.type == type:
                flash('Type Already Present', category='danger')
                return redirect(url_for('main.add_software_type'))

        type = SoftwareTypes(type=type, instances=0, org_id=org.id)

        db.session.add(type)
        db.session.commit()

        return redirect(url_for('main.add_software_type'))

    return render_template('add_software_type.html', org=org, form=form)

@main.route('/add_language', methods=['GET', 'POST'])
@login_required
@org_required
def add_language():
    form = AddLanguageForm()

    org = Organizations.query.get(current_user.organization_id)

    if form.validate_on_submit():
        lang = form.lang.data

        for dblang in org.languages:
            if lang == dblang.name:
                flash('Language Already Present', category='danger')
                return redirect(url_for('main.add_language'))
            
        lang = Languages(name=lang, instances=0, org_id=org.id)

        db.session.add(lang)
        db.session.commit()

        return redirect(url_for('main.add_language'))
    
    return render_template('add_language.html', org=org, form=form)

@main.route('/add_software', methods=['GET', 'POST'])
@login_required
@org_required
def add_software():
    form = AddSoftwareForm()

    org = Organizations.query.get(current_user.organization_id)

    form.clusters.choices = [(cluster.id, cluster.name + ' ({}:{})'.format(cluster.es_host, cluster.es_port)) for cluster in org.clusters]

    form.software_type.choices = [(software_type.type, software_type.type) for software_type in org.software_types]

    form.languages.choices = [(lang.name, lang.name) for lang in org.languages]

    if form.validate_on_submit():
        doc = {'software_type': form.software_type.data, 
               'languages': form.languages.data, 
               'name': form.name.data, 
               'description': form.description.data, 
               'retrieval_instructions': form.retrieval_instructions.data}

        for cluster_id in form.clusters.data:
            cluster = Clusters.query.get(cluster_id)

            es = get_es_connection(host=cluster.es_host,
                                   port=cluster.es_port,
                                   secure=cluster.secure,
                                   org_name=org.name,
                                   username=cluster.es_user,
                                   password=cluster.es_password,
                                   app=current_app)

            es.index(index='software-index', document=doc)
            
        return redirect(url_for('main.add_software'))

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
    
    if es.ping():
        flash("Connection Verified", category='success')
    else:
        flash("Connection Failed", category='danger')

    return redirect(url_for('main.clusters'))

@main.route('/clusters', methods=['GET', 'POST'])
@login_required
@org_required
def clusters(): 
    form = AddClusterForm()

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
