from datetime import datetime, timedelta

from flask import Blueprint, render_template, current_app, flash, url_for, redirect
from flask.ext.login import login_required
from flask.ext.babel import gettext as _

from ..extensions import db
from sqlalchemy.sql import func

from ..campaign.models import TwilioPhoneNumber, Campaign
from ..call.models import Call
from ..campaign.constants import STATUS_PAUSED
from ..api.constants import API_TIMESPANS
from ..utils import get_one_or_create

admin = Blueprint('admin', __name__, url_prefix='/admin')


# all admin routes require login
@admin.before_request
@login_required
def before_request():
    pass


@admin.route('/')
def dashboard():
    campaigns = Campaign.query.filter(Campaign.status_code >= STATUS_PAUSED)
    calls_by_campaign = (db.session.query(Campaign.id, func.count(Call.id))
            .filter(Campaign.status_code >= STATUS_PAUSED)
            .join(Call).group_by(Campaign.id))

    calls_by_day = (db.session.query(func.date(Call.timestamp), func.count(Call.id))
            .group_by(func.date(Call.timestamp)))

    active_phone_numbers = TwilioPhoneNumber.query.all()

    return render_template('admin/dashboard.html',
        campaigns=campaigns,
        calls_by_campaign=dict(calls_by_campaign.all()),
        calls_by_day=calls_by_day.all(),
        active_phone_numbers=active_phone_numbers
    )


@admin.route('/statistics')
def statistics():
    campaigns = Campaign.query.all()
    today = datetime.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return render_template('admin/statistics.html',
        campaigns=campaigns, timespans=API_TIMESPANS,
        this_week_start=start.strftime('%Y-%m-%d'),
        this_week_end=end.strftime('%Y-%m-%d'))


@admin.route('/system')
def system():
    twilio_numbers = TwilioPhoneNumber.query.all()
    admin_api_key = current_app.config.get('ADMIN_API_KEY')
    return render_template('admin/system.html',
                           message_defaults=current_app.config.CAMPAIGN_MESSAGE_DEFAULTS,
                           twilio_numbers=twilio_numbers,
                           twilio_auth=current_app.config.get('TWILIO_CLIENT').auth,
                           admin_api_key=admin_api_key)


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

    # find any stale numbers we have in the db that aren't in the response
    stale_numbers = TwilioPhoneNumber.query.filter(
        TwilioPhoneNumber.number.notin_([n.phone_number for n in twilio_numbers]))
    # and remove them
    # TODO, check if delete will cascade to campaign
    for num in stale_numbers.all():
        deleted_numbers.append(num.phone_number)
        db.session.delete(num)
    db.session.commit()

    if new_numbers:
        flash(_("Added Twilio Number: ") + ', '.join(new_numbers), 'success')
    if deleted_numbers:
        flash(_("Removed Twilio Number: ") + ', '.join(deleted_numbers), 'warning')
    else:
        flash(_("Twilio Numbers are Up to Date"), 'success')

    return redirect(url_for('admin.system'))
