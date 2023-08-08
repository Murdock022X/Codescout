from flask import render_template, Blueprint, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from website.auth.forms import SignupForm, LoginForm
from website import db
from website.models import Users, Organizations

auth = Blueprint('auth', __name__)

# Login route.
@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route to login Flask user.
    
    :return: Redirect to main.index or rendered template of login.html.
    """

    form = LoginForm()

    # Need to pass organization, if user is associated with one, to render template.
    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    # Login the user if they provided valid information.
    if form.validate_on_submit():

        # Check if the username is already in the database, if it is we need 
        # to check password.
        user = Users.query.filter_by(username=form.username.data).first()

        # If user exists.
        if user:
            # If password is correct login the user and redirect to main.index.
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect(url_for('main.index'))
            
            else:
                flash('Incorrect password')

        else:
            flash('User does not exist')

    return render_template('login.html', form=form, org=org)

# Signup route.
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Signup user as a Flask user.

    :return: Rendered template for signup.html or redirect to auth.login.
    """

    form = SignupForm()

    # Need to pass organization, if user is associated with one, to render 
    # template.
    org = None
    if current_user.is_authenticated and current_user.organization_id:
        org = Organizations.query.get(current_user.organization_id)

    # Do the necessary verification to ensure that the form data supplied can 
    # create a user and then create if valid.
    if form.validate_on_submit():

        # If username already take it can't be used again.
        if Users.query.filter_by(username=form.username.data).first():
            flash('Email Already Registered')
            
        # Add the user.
        else:

            # Create the password hash.
            password_hash = generate_password_hash(form.password.data, 
                                                   method='sha256')
            
            # Add the new user.
            new_user = Users(username=form.username.data, 
                            password_hash=password_hash, 
                            first_name=form.first_name.data, 
                            last_name=form.last_name.data,
                            admin_status=False)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('auth.login'))

    return render_template('signup.html', form=form, org=org)

# Logout the current user.
@auth.route('/logout')
@login_required
def logout():
    """
    Logout current user.

    :return: Redirect to main.index.
    """
    logout_user()
    return redirect(url_for('main.index'))
