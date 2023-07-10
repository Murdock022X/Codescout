from flask import render_template, Blueprint, redirect, url_for, flash, session

from flask_login import login_user, logout_user, login_required, current_user

from website.auth.forms import SignupForm, LoginForm

from website import db

from werkzeug.security import generate_password_hash, check_password_hash

from website.models import Users, Organizations

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()

        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)

                return redirect(url_for('main.index'))
            
            else:
                flash('Incorrect password')

        else:
            flash('User does not exist')

    return render_template('login.html', form=form, org=org)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    if form.validate_on_submit():
        if Users.query.filter_by(username=form.username.data).first():
            flash('Email Already Registered')
            
        else:
            password_hash = generate_password_hash(form.password.data, 
                                                   method='sha256')
            
            new_user = Users(username=form.username.data, 
                            password_hash=password_hash, 
                            first_name=form.first_name.data, 
                            last_name=form.last_name.data,
                            admin_status=False)

            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('auth.login'))

    return render_template('signup.html', form=form, org=org)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
