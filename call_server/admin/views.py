from flask import Blueprint, render_template
from flask.ext.login import login_required

admin = Blueprint('admin', __name__)


@admin.route('/admin')
@login_required
def admin_dash():
    return render_template('admin/dashboard.html')
