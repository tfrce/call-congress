from flask import Blueprint, render_template, current_app, flash, url_for, redirect
from flask.ext.login import login_required
from flask.ext.babel import gettext as _

from twilio.rest import TwilioRestClient

from ..extensions import db

from ..campaign.models import TwilioPhoneNumber, Campaign
from ..call.models import Call
from ..campaign.constants import PAUSED
from ..utils import get_one_or_create

admin = Blueprint('admin', __name__, url_prefix='/admin')

# all admin routes require login
@admin.before_request
@login_required
def before_request():
    pass


@admin.route('/')
def dashboard():
    campaigns = Campaign.query.filter(Campaign.status_code >= PAUSED)
    return render_template('admin/dashboard.html', campaigns=campaigns)


@admin.route('/statistics')
def statistics():
    data = {}
    data['calls_by_campaign'] = (db.session.query(
        db.func.Count(Call.id))
        .group_by(Call.campaign_id).all()
    )[0][0]

    data['campaigns'] = len(Campaign.query.all())

    data['unique_users'] = (db.session.query(Call)
        .distinct(Call.phone_hash)
        .group_by(Call.phone_hash)
    ).count()

    return render_template('admin/statistics.html', data=data)


@admin.route('/system')
def system():
    twilio_numbers = TwilioPhoneNumber.query.all()
    return render_template('admin/system.html',
                           message_defaults=current_app.config.CAMPAIGN_MESSAGE_DEFAULTS,
                           twilio_numbers=twilio_numbers,
                           twilio_auth=current_app.config.get('TWILIO_CLIENT').auth)


@admin.route('/twilio/resync', methods=['POST'])
def twilio_resync():
    """ One-way sync of Twilio numbers from REST Client down to our database
    Adds new numbers, saves voice_application_sid, and removes stale entries."""

    client = current_app.config.get('TWILIO_CLIENT')
    twilio_numbers = client.phone_numbers.list()

    new_numbers = []
    deleted_numbers = []
    for num in twilio_numbers:
        obj, created = get_one_or_create(db.session, TwilioPhoneNumber,
                                         number=num.phone_number,
                                         twilio_sid=num.sid)
        if created:
            new_numbers.append(num.phone_number)

        # update voice application sid from twilio
        obj.twilio_app = num.voice_application_sid
        db.session.add(obj)
        db.session.commit()

    # TODO, find any stale numbers we have in the db that aren't in the response
    # and remove them

    if new_numbers:
        flash(_("Added Twilio Number: ") + ', '.join(new_numbers), 'success')
    else:
        flash(_("Twilio Numbers are Up to Date"), 'success')

    return redirect(url_for('admin.system'))
