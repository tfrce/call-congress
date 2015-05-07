from flask import (Blueprint, render_template, current_app, request,
                   flash, url_for, redirect, session, abort)
from flask.ext.login import login_required

campaign = Blueprint('campaign', __name__, url_prefix='/campaign')


@campaign.route('/')
@login_required
def index():
    page = int(request.args.get('page', 1))
    pagination = Campaign.query.paginate(page=page, per_page=10)
    return render_template('campaign/list.html', pagination=pagination)


@campaign.route('/new')
@login_required
def new():
    return render_template('campaign/new.html')


@campaign.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit():
    return render_template('campaign/new.html')
