from flask import Blueprint, render_template, current_app

site = Blueprint('site', __name__, )


@site.route('/')
def index():
    INSTALLED_ORG = current_app.config.get('INSTALLED_ORG', '<YOUR ORG NAME>')
    return render_template('site/index.html', INSTALLED_ORG=INSTALLED_ORG)
