from flask_login import current_user
from flask import request, redirect, url_for, flash

from functools import wraps

def org_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if current_user.org_status != 1:
            flash('You need to join an organization to use that.', category='danger')
            return redirect(url_for('main.join_organization', next=request.url))
        return f(*args, **kwargs)
    return decorated_func

def admin_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.admin_status:
            flash('You need to be an organization admin to use that.', category='danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_func