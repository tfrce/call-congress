from flask import (Blueprint, render_template, current_app, request,
                   flash, url_for, redirect, session, abort)
from flask.ext.login import login_required

import json

from ..extensions import db

from .constants import CAMPAIGN_NESTED_CHOICES
from .models import Campaign
from .forms import CampaignForm

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
    form = CampaignForm()

    if form.validate_on_submit():
        campaign = Campaign()
        form.populate_obj(campaign)

        db.session.add(campaign)
        db.session.commit()

        flash('Campaign created.', 'success')

    return render_template('campaign/form.html', form=form,
                           CAMPAIGN_NESTED_CHOICES=CAMPAIGN_NESTED_CHOICES)


@campaign.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit():
    return render_template('campaign/new.html')


@campaign.route('/<int:user_id>/record', methods=['GET', 'POST'])
@login_required
def record():
    return render_template('campaign/record.html')
