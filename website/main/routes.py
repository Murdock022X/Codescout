from flask import Blueprint, render_template, redirect, url_for

main = Blueprint('main', __name__)

@main.route('/index')
def index():
    pass

@main.route('/package-search-engine', methods=['GET', 'POST'])
def search_engine():
    pass
