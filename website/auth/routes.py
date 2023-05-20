from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    pass

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    pass

@auth.route('/logout')
@login_required
def logout():
    pass
