from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from .forms import SignupForm, LoginForm

from website import db

from werkzeug.security import generate_password_hash, check_password_hash

from website.database_models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()

        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect('main.search_engine')
            
            else:
                flash('Incorrect password')

        else:
            flash('User does not exist')

    return render_template('login.html', form=form)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).one():
            flash('Username Taken')
        else:
            password_hash = generate_password_hash(form.password.data, method='sha256')
            new_user = User(username=form.username.data, password_hash=password_hash, first_name=form.first_name.data, last_name=form.last_name.data)

            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('auth.login'))

    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('main.index')
