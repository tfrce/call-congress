from flask import Blueprint, render_template, current_app, flash, url_for, redirect
from flask.ext.login import login_required
from flask.ext.babel import gettext as _

from twilio.rest import TwilioRestClient

from ..extensions import db

from ..campaign.models import TwilioPhoneNumber
from ..utils import get_one_or_create

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
    twilio_numbers = TwilioPhoneNumber.query.all()
    print twilio_numbers
    return render_template('admin/system.html',
                           twilio_numbers=twilio_numbers,
                           twilio_auth=current_app.config.get('TW_CLIENT').auth)


@admin.route('/twilio/resync', methods=['POST'])
@login_required
def twilio_resync():
    """ One-way sync of Twilio numbers from REST Client down to our database
    Adds new numbers, saves voice_application_sid, and removes stale entries."""

    client = current_app.config.get('TW_CLIENT')
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
