from flask import Blueprint, render_template, redirect, url_for

from forms import SearchForm

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/search_engine', methods=['GET', 'POST'])
def search_engine():
    form = SearchForm()

    if form.validate_on_submit():
        clusters = form.cluster_selections.data

        search_type = form.search_type.data

        search_query = form.search_query.data

    return render_template('search_engine.html', form=form)
