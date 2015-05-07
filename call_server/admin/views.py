from flask import Blueprint, render_template
from flask.ext.login import login_required

admin = Blueprint('admin', __name__, url_prefix='/admin')


@admin.route('/')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')


@admin.route('/statistics')
@login_required
def statistics():
    return render_template('admin/statistics.html')


@admin.route('/system')
@login_required
def system():
    return render_template('admin/system.html')
