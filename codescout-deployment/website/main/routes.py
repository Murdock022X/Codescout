from flask import render_template, Blueprint, redirect, url_for, current_app, flash
from flask_login import current_user, login_required

from website import db
from website.models import Users, Clusters, SoftwareTypes, Languages, \
Organizations
from website.main.forms import CreateOrgForm, JoinOrgForm, SearchForm, \
AddClusterForm, AddSoftwareForm, AddSoftwareTypeForm, AddLanguageForm
from website.main.decorators import org_required, admin_required, org_cluster_required
from website.main.utils import get_es_connection

from elastic_transport import ConnectionError
from elasticsearch import BadRequestError

from cryptography.fernet import Fernet

from secrets import token_hex

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    """
    Flask route that returns webpage for info on the project.

    :return: Rendered index.html webpage.
    """

    # Typical organization check.
    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    return render_template('index.html', org=org)

@main.route('/join_organization', methods=['GET', 'POST'])
@login_required
def join_organization():
    """
    Flask route that allows user to join organization using enrollment token.

    :return: Rendered join_org.html webpage, could also be a redirect to this route.
    """
    
    # Form takes enrollment token as input.
    form = JoinOrgForm()

    # Typical organization check.
    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    # If form is submitted and valid.
    if form.validate_on_submit():

        # Match enrollment token against organizations.
        org = Organizations.query.filter_by(enrollment_token=form.org_token.data).first()

        # If no organization is found flash invalid and reload the page.
        if not org:
            flash('Invalid token', category='danger')
            return redirect(url_for('main.join_organization'))

        # Change the users organization to match the found organization.
        current_user.organization_id = org.id

        db.session.commit()

        flash('Successfully joined organization {}.'.format(org.name), 'success')

    return render_template('join_org.html', form=form, org=org)

@main.route('/create_organization', methods=['GET', 'POST'])
@login_required
def create_organization():
    """
    Create an organization.

    :return: Rendered add_org.html template.
    """

    # Form accepts name of organization.
    form = CreateOrgForm()

    # If form submitted and valid.
    if form.validate_on_submit():

        # Create organization object and commit to database.
        org = Organizations(name=form.org_name.data, enrollment_token=token_hex(32))
        db.session.add(org)
        db.session.commit()

        # Add the user who created the organization as the admin.
        current_user.org_status = 1
        current_user.organization_id = org.id
        current_user.admin_status = True

        db.session.commit()

        flash('Organization created and joined, you are now the primary admin.', category='success')

    # Requery to check if there is an organization now.
    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    return render_template('add_org.html', form=form, org=org)

@main.route('/org_user_monitor/<int:page>')
@login_required
@org_required
@admin_required
def org_user_monitor(page):
    """
    Page that shows all users in organization, allows you to remove them and displays the enrollment token.

    :param page: Page determines data to show in pagination.
    """

    # Query for org, don't need checks because of org_required.
    org = Organizations.query.get(current_user.organization_id)

    # Get how many results should be displayed per page.
    page_len = current_app.config['USER_PAGE_LEN']

    # Get the users of the organization.
    org_users = org.users

    # Figure out the total number of pages.
    total_pages = len(org_users) // page_len
    if len(org_users) % page_len != 0:
        total_pages += 1

    # Assemble the data for the page into one list.
    users = []
    for i in range(page * page_len, page * page_len + page_len):
        if i >= len(org_users):
            break
        users.append(org_users[i])

    return render_template('user_monitor.html', org=org, users=users, page=page, total_pages=total_pages)

@main.route('/generate_new_token')
@login_required
@org_required
@admin_required
def generate_new_token():
    """
    Route that generates a new organization enrollment token.

    :return: Redirect to user monitor page.
    """
    org = Organizations.query.get(current_user.organization_id)

    org.enrollment_token = token_hex(32)
    db.session.commit()

    return redirect(url_for('main.org_user_monitor', page=0))

@main.route('/remove_user/<int:user_id>')
@login_required
@org_required
@admin_required
def remove_user(user_id):
    """
    Remove user from organization.

    :param user_id: The database id for the user to be removed.
    :return: Redirect to user monitor page.
    """
    user = Users.query.get(user_id)

    user.org_status = 0
    user.organization_id = None

    db.session.add(user)
    db.session.commit()

    flash('User deleted.', category='success')

    return redirect(url_for('main.org_user_monitor', page=0))

@main.route('/search_engine', methods=['GET', 'POST'])
@login_required
@org_cluster_required
def search_engine():
    """
    Webpage that processes search requests.

    :return: Rendered template for search_engine.html or redirect to 
    search results route.
    """

    # Typical organization check.
    org = Organizations.query.get(current_user.organization_id)

    form = SearchForm()

    # Fill filter choices for software_type and language.
    form.software_type.choices = [sw.type for sw in org.software_types]
    form.language.choices = [lang.name for lang in org.languages]

    # If form is submitted and valid.
    if form.validate_on_submit():

        # Get the query, language, and software type.
        software_type = form.software_type.data
        query = form.search_query.data
        language = form.language.data

        # Check if we recieved a query, if not we will get all results.
        q_check = True
        if len(query) == 0:
            q_check = False
            query = "match_all"

        # Check if we recieved a valid choice for software type.
        sw_check = True
        if software_type is None:
            sw_check = False
            software_type = 'None'
        
        # Check if we recieved a valid choice for language.
        lang_check = True
        if language is None:
            lang_check = False
            language = 'None'

        # Redirect to search results page.
        return redirect(url_for('main.search_results', page=0, q_check=q_check, q=query, sw_check=sw_check, sw=software_type, lang_check=lang_check, lang=language))

    # Render search engine page.
    return render_template('search_engine.html', form=form, org=org)

@main.route('/search_results/<int:page>/<int:q_check>/<q>/<int:sw_check>/<sw>/<int:lang_check>/<lang>')
@login_required
@org_cluster_required
def search_results(page, q_check, q, sw_check, sw, lang_check, lang):
    """
    Gather search results from Elasticsearch cluster and display in a pagination.

    :param page: The page number for the pagination.
    :param q_check: 0 if there is no query, 1 if there is a query.
    :param q: Query to match in the Elasticsearch cluster.
    :param sw_check: 0 if there is no software type, 1 if there is a software type.
    :param sw: The software type filter value.
    :param lang_check: 0 if there is no language, 1 if there is a language.
    :param lang: The language filter value.
    :return: Rendered search_results.html template.
    """
    
    # Convert check variables to bool.
    q_check = bool(q_check)
    sw_check = bool(sw_check)
    lang_check = bool(lang_check)

    # Get the organization and cluster.
    org = Organizations.query.get(current_user.organization_id)
    cluster = Clusters.query.get(org.cluster_id)

    # Generate the search query dict.
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

    # Get a connection to Elasticsearch.
    es = get_es_connection(
        host=cluster.es_host,
        port=cluster.es_port,
        username=cluster.es_user,
        password=cluster.es_password,
        enc_key=current_app.config["ENCRYPTION_KEY"]
    )

    # Search the Elasticsearch index for matches.
    response = es.search(index="software-index", query=search_query)
    
    # Take response data and run it through the filters, if it meets both 
    # criteria add it to the data.
    valid_data = []
    for entry in response['hits']['hits']:
        if sw_check:
            if entry['_source']['software_type'] != sw:
                continue
        
        if lang_check:
            if entry['_source']['language'] != lang:
                continue
        
        valid_data.append(entry)

    # Calculate total number of pages for the pagination.
    total_pages = len(valid_data) // current_app.config['SEARCH_PAGE_LEN']
    if len(valid_data) % current_app.config['SEARCH_PAGE_LEN'] > 0:
        total_pages += 1

    # Take the pagination for the page.
    page_data = valid_data[page * current_app.config["SEARCH_PAGE_LEN"]:page * current_app.config["SEARCH_PAGE_LEN"] + current_app.config["SEARCH_PAGE_LEN"]]

    return render_template('search_results.html', org=org, page_data=page_data, page=page, q_check=q_check, q=q, sw_check=sw_check, sw=sw, lang_check=lang_check, lang=lang, total_pages=total_pages)

@main.route('/software_info/<es_id>')
@login_required
@org_cluster_required
def software_info(es_id):
    """
    Route that gets information about Elasticsearch results.

    :param es_id: The Elasticsearch id for information we should retrieve.
    :return: Return rendered software_info.html template.
    """

    # Get the organization and cluster.
    org = Organizations.query.get(current_user.organization_id)
    cluster = Clusters.query.get(org.cluster_id)

    # Get the Elasticsearch connection.
    es = get_es_connection(
        host=cluster.es_host,
        port=cluster.es_port,
        username=cluster.es_user,
        password=cluster.es_password,
        enc_key=current_app.config["ENCRYPTION_KEY"]
    )

    # Get the response by getting from _id.
    response = es.search(index='software-index', query={"term": {"_id": es_id}})

    # Get the item.
    item = response['hits']['hits'][0]['_source']

    return render_template('software_info.html', org=org, item=item)

@main.route('/add_software_type', methods=['GET', 'POST'])
@login_required
@org_required
def add_software_type():
    """
    Add a software type under the current users organization to the database.

    :return: Either redirect to reload page or render add_software_type.html.
    """

    # Get form and organization.
    form = AddSoftwareTypeForm()
    org = Organizations.query.get(current_user.organization_id)

    # If form is submitted and valid.
    if form.validate_on_submit():

        # Get the software type and check if the type is already present in 
        # database.
        type = form.type.data
        for swt in org.software_types:
            if swt.type == type:
                flash('Type Already Present', category='danger')
                return redirect(url_for('main.add_software_type'))

        # Create the new software type.
        type = SoftwareTypes(type=type, org_id=org.id)
        db.session.add(type)
        db.session.commit()

        return redirect(url_for('main.add_software_type'))

    return render_template('add_software_type.html', org=org, form=form)

@main.route('/add_language', methods=['GET', 'POST'])
@login_required
@org_required
def add_language():
    """
    Add a language under the current users organization to the database.

    :return: Either redirect to reload page or render add_language.html.
    """

    # Get form and organization.
    form = AddLanguageForm()
    org = Organizations.query.get(current_user.organization_id)

    # If form is submitted and valid.
    if form.validate_on_submit():

        # Get the language and check if the type is already present in 
        # database.
        lang = form.lang.data
        for dblang in org.languages:
            if lang == dblang.name:
                flash('Language Already Present', category='danger')
                return redirect(url_for('main.add_language'))
            
        # Add language to database.
        lang = Languages(name=lang, org_id=org.id)
        db.session.add(lang)
        db.session.commit()

        return redirect(url_for('main.add_language'))
    
    return render_template('add_language.html', org=org, form=form)

@main.route('/add_software', methods=['GET', 'POST'])
@login_required
@org_cluster_required
def add_software():
    """
    Route to add software to cluster.

    :return: Rendered add_software.html template, or redirect to reload.
    """

    # Get form and organization.
    form = AddSoftwareForm()
    org = Organizations.query.get(current_user.organization_id)

    # Set dynamic choices for software types and languages.
    form.software_type.choices = [(software_type.type, software_type.type) for software_type in org.software_types]
    form.language.choices = [(lang.name, lang.name) for lang in org.languages]

    # If form is submitted and valid.
    if form.validate_on_submit():

        # Generate the document to submit.
        doc = {'software_type': form.software_type.data, 
               'language': form.language.data, 
               'name': form.name.data, 
               'description': form.description.data, 
               'install_instructions': form.install_instructions.data}

        # Get the cluster and get a connection to it.
        cluster = Clusters.query.get(org.cluster_id)
        es = get_es_connection(host=cluster.es_host,
                                port=cluster.es_port,
                                username=cluster.es_user,
                                password=cluster.es_password,
                                enc_key=current_app.config["ENCRYPTION_KEY"])

        # Add document to index.
        es.index(index='software-index', document=doc)
            
        return redirect(url_for('main.add_software'))

    return render_template('add_software.html', form=form, org=org)

@main.route('/clusters', methods=['GET', 'POST'])
@login_required
@org_required
def clusters():
    """
    Modify/view cluster attributes.

    :return: Redirect to reload page or rendered clusters.html page.
    """

    # Get form and organization.
    form = AddClusterForm()
    org = Organizations.query.get(current_user.organization_id)

    # Check if a cluster exists for your organization, get it if it does.
    cluster = None
    if org.cluster_id:
        cluster = Clusters.query.get(org.cluster_id)

    # If form is submitted and valid.
    if form.validate_on_submit():

        # Get encryption key and create Fernet object from it.
        key = current_app.config["ENCRYPTION_KEY"]
        f = Fernet(key.encode(encoding="utf8"))

        # Get form data, encrypt password input.
        name = form.name.data
        es_host = form.es_host.data
        es_port = form.es_port.data
        es_user = form.es_user.data
        es_password = f.encrypt(form.es_password.data.encode(encoding="utf8")).decode(encoding="utf8")

        # If there is no previous cluster we need to create a new cluster object.
        if cluster is None:
            cluster = Clusters(
                name=name, 
                es_host=es_host, 
                es_port=es_port, 
                es_user=es_user, 
                es_password=es_password, 
                org_id=org.id
            )
            db.session.add(cluster)
            
        # Else we can just modify the attributes to be the new attributes.
        else:
            cluster.name = name
            cluster.es_host = es_host
            cluster.es_port = es_port
            cluster.es_user = es_user
            cluster.es_password = es_password

        # Add.
        db.session.commit()
        
        # Get new id and set the organization cluster id to be the correct id.
        org.cluster_id = cluster.id
        db.session.commit()

        return redirect(url_for('main.clusters'))

    return render_template('clusters.html', form=form, org=org, cluster=cluster)

@main.route('/delete_cluster/<int:cluster_id>')
@login_required
@org_required
@admin_required
def delete_cluster(cluster_id):
    """
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
    """
    Route that tests connection to Elasticsearch cluster setup.

    :param cluster_id: The id for the cluster to test.
    :return: Redirect to main.clusters.
    """

    # Get cluster and connection.
    cluster = Clusters.query.get(cluster_id)
    es = get_es_connection(host=cluster.es_host, 
                            port=cluster.es_port, 
                            username=cluster.es_user, 
                            password=cluster.es_password,
                            enc_key=current_app.config["ENCRYPTION_KEY"])
    
    if es.info():
        flash("Connection Test Successful", category='success')
        
    else:
        flash("Connection Test Failed", category='danger')

    return redirect(url_for('main.clusters'))

@main.route('/setup_elastic/<int:cluster_id>')
@login_required
@org_required
def setup_elastic(cluster_id: int):
    """
    Auto setup Elasticsearch software-index index. Index used for Flask App documents.

    :param cluster_id: The id for the cluster to test.
    :return: Redirect to main.clusters.
    """

    # Get cluster and connection.
    cluster = Clusters.query.get(cluster_id)
    es = get_es_connection(host=cluster.es_host, 
                            port=cluster.es_port, 
                            username=cluster.es_user, 
                            password=cluster.es_password,
                            enc_key=current_app.config["ENCRYPTION_KEY"])
    
    # Try to create index.
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
