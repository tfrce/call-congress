from flask import Blueprint, render_template, jsonify

admin = Blueprint('admin', __name__)


@admin.route('/admin')
def admin_home():
    return render_template('admin.html')


@admin.route('/admin/legislators.json')
def admin_legislators():
    return jsonify(data.legislators)
