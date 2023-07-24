from flask import render_template, Blueprint, redirect, url_for, current_app, flash, request, session
from flask_login import current_user, login_required

from website.models import Users, Clusters, SoftwareTypes, Languages, \
Organizations

from werkzeug.utils import secure_filename

from website.main.forms import CreateOrgForm, JoinOrgForm, SearchForm, \
AddClusterForm, EditClusterForm, AddSoftwareForm, AddSoftwareTypeForm, \
AddLanguageForm

from website import db

from website.main.decorators import org_required, admin_required
from website.main.utils import save_certs, get_es_connection, get_from_and_size, url_serialize, url_deserialize

from elastic_transport import ConnectionError

from elasticsearch import BadRequestError

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

        current_user.org_status = 1
        current_user.organization_id = org.id
        current_user.admin_status = True

        db.session.commit()

        flash('Organization created and joined, you are now the primary admin.', category='success')

    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    return render_template('add_org.html', form=form, org=org)

@main.route('/org_user_monitor')
@login_required
@org_required
@admin_required
def org_user_monitor():
    org = Organizations.query.get(current_user.organization_id)

    users = org.users

    return render_template('user_monitor.html', org=org, users=users)

@main.route('/search_org_users/<query>')
@login_required
@org_required
@admin_required
def search_org_users(query: str):
    results = []

    org = Organizations.query.get(current_user.organization_id)

    for user in org.users:
        if query.lower() in user.name.lower():
            results.append(user)

    return results

@main.route('/remove_user/<int:user_id>')
@login_required
@org_required
@admin_required
def remove_user(user_id):
    user = Users.query.get(user_id)

    user.organization_id = None

    db.session.commit()

    return redirect(url_for('main.org_user_monitor'))

@main.route('/search_engine', methods=['GET', 'POST'])
@login_required
@org_required
def search_engine():
    org = Organizations.query.get(current_user.organization_id)

    form = SearchForm()

    form.software_type.choices = [sw.type for sw in org.software_types]

    form.language.choices = [lang.name for lang in org.languages]

    if form.validate_on_submit():

        software_type = form.software_type.data
        query = form.search_query.data
        language = form.language.data

        print ('0', query, '0')
        q_check = True
        if len(query) == 0:
            q_check = False
            query = "match_all"

        sw_check = True
        if software_type is None:
            sw_check = False
            software_type = 'None'
        
        lang_check = True
        if language is None:
            lang_check = False
            language = 'None'

        return redirect(url_for('main.search_results', page=0, q_check=q_check, q=query, sw_check=sw_check, sw=software_type, lang_check=lang_check, lang=language))

    return render_template('search_engine.html', form=form, org=org)

@main.route('/search_results/<int:page>/<int:q_check>/<q>/<int:sw_check>/<sw>/<int:lang_check>/<lang>')
@login_required
@org_required
def search_results(page, q_check, q, sw_check, sw, lang_check, lang):
    q_check = bool(q_check)
    sw_check = bool(sw_check)
    lang_check = bool(lang_check)

    org = Organizations.query.get(current_user.organization_id)

    cluster = Clusters.query.get(org.cluster_id)

    search_query = {"match_all": {}}

    if q_check:
        search_query = \
        {
            "match": 
            {
                "description":
                {
                    "query": q
                }
            }
        }

    es = get_es_connection(
        host=cluster.es_host,
        port=cluster.es_port,
        secure=cluster.secure,
        org_name=org.name,
        username=cluster.es_user,
        password=cluster.es_password,
        app=current_app
    )

    response = es.search(index="software-index", query=search_query)
    
    valid_data = []

    for entry in response['hits']['hits']:
        if sw_check:
            if entry['_source']['software_type'] != sw:
                print(0)
                continue
        
        if lang_check:
            if entry['_source']['language'] != lang:
                print(1)
                continue
        
        valid_data.append(entry)

    total_pages = len(valid_data) // current_app.config['SEARCH_PAGE_LEN']

    if len(valid_data) % current_app.config['SEARCH_PAGE_LEN'] > 0:
        total_pages += 1

    page_data = valid_data[page * current_app.config["SEARCH_PAGE_LEN"]:page * current_app.config["SEARCH_PAGE_LEN"] + current_app.config["SEARCH_PAGE_LEN"]]

    return render_template('search_results.html', org=org, page_data=page_data, page=page, q_check=q_check, q=q, sw_check=sw_check, sw=sw, lang_check=lang_check, lang=lang, total_pages=total_pages)

@main.route('/software_info/<es_id>')
@login_required
@org_required
def software_info(es_id):

    org = Organizations.query.get(current_user.organization_id)

    cluster = Clusters.query.get(org.cluster_id)

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

        type = SoftwareTypes(type=type, org_id=org.id)

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
            
        lang = Languages(name=lang, org_id=org.id)

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

    form.software_type.choices = [(software_type.type, software_type.type) for software_type in org.software_types]

    form.language.choices = [(lang.name, lang.name) for lang in org.languages]

    if form.validate_on_submit():
        doc = {'software_type': form.software_type.data, 
               'language': form.language.data, 
               'name': form.name.data, 
               'description': form.description.data, 
               'install_instructions': form.retrieval_instructions.data}

        cluster = Clusters.query.get(org.cluster_id)

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

@main.route('/clusters', methods=['GET', 'POST'])
@login_required
@org_required
def clusters(): 
    form = AddClusterForm()

    org = Organizations.query.get(current_user.organization_id)

    cluster = None
    if org.cluster_id:
        cluster = Clusters.query.get(org.cluster_id)

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

        if cluster is None:
            cluster = Clusters(
                name=name, 
                es_host=es_host, 
                es_port=es_port, 
                es_user=es_user, 
                es_password=es_password, 
                secure=sb,
                org_id=org.id
            )
            db.session.add(cluster)

        else:
            cluster.name = name
            cluster.es_host = es_host
            cluster.es_port = es_port
            cluster.es_user = es_user
            cluster.es_password = es_password
            cluster.secure = sb

        db.session.commit()

        org.cluster_id = cluster.id

        db.session.commit()

        save_certs(certs_file=form.es_certs_file, app=current_app, 
                   host=es_host, org_name=org.name)
        
        flash('Cluster configuration updated.', category='success')

        return redirect(url_for('main.clusters'))

    return render_template('clusters.html', form=form, org=org, cluster=cluster)

@main.route('/delete_cluster/<int:cluster_id>')
@login_required
@org_required
@admin_required
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
        flash("Connection Test Successful", category='success')
    else:
        flash("Connection Test Failed", category='danger')

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
    
    try:
        es.indices.create(index='software-index')
        es.indices.create(index='org-search-index')
    except ConnectionError:
        flash('Connection Failed', category='danger')
    except ValueError:
        flash('Invalid Cluster', category='danger')
    except BadRequestError:
        flash('Index Already Exists', category='danger')
    else:
        flash('Cluster Configured Successfully', category='success')

    return redirect(url_for('main.clusters'))
