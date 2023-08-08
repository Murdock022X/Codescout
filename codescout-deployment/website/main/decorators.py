from flask_login import current_user
from flask import request, redirect, url_for, flash
from website.models import Organizations
from functools import wraps

# Decorator ensures that when accessing a flask route that requires that user 
# has joined an organization the user meets the criteria.
def org_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if current_user.organization_id is None:
            flash('You need to join an organization to use that.', category='danger')
            return redirect(url_for('main.join_organization', next=request.url))
        return f(*args, **kwargs)
    return decorated_func

# Decorator ensures that when accessing a flask route that requires that user 
# is an admin the user meets the criteria.
def admin_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.admin_status:
            flash('You need to be an organization admin to use that.', category='danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_func

# Decorator ensures that when accessing a flask route that requires that user 
# has joined an organization and that organization has set a cluster for use, 
# the user meets the criteria.
def org_cluster_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        org = None
        if current_user.organization_id is not None:
            org = Organizations.query.get(current_user.organization_id)
        else:
            flash('Please join an organization to use that.', category='danger')
            return redirect(url_for('main.index'))
        if not org.cluster_id:
            flash('Your organization needs to setup a cluster to use that, contact your admin.', category='danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_func
