from flask import (Blueprint, render_template, current_app, request,
                   flash, url_for, redirect, session, abort, jsonify)
from flask.ext.login import login_required

import sqlalchemy

from ..extensions import db
from ..utils import choice_items, choice_keys, choice_values_flat

from .constants import CAMPAIGN_NESTED_CHOICES, CUSTOM_CAMPAIGN_CHOICES, EMPTY_CHOICES, LIVE
from .models import Campaign, Target, CampaignTarget, AudioRecording, CampaignAudioRecording
from .forms import (CampaignForm, CampaignAudioForm, AudioRecordingForm,
                    CampaignLaunchForm, CampaignStatusForm, TargetForm)

campaign = Blueprint('campaign', __name__, url_prefix='/admin/campaign')


@campaign.before_request
@login_required
def before_request():
    # all campaign routes require login
    pass


@campaign.route('/')
def index():
    campaigns = Campaign.query.all()
    return render_template('campaign/list.html', campaigns=campaigns)


@campaign.route('/create', methods=['GET', 'POST'])
@campaign.route('/<int:campaign_id>/edit', methods=['GET', 'POST'])
def form(campaign_id=None):
    edit = False
    if campaign_id:
        edit = True

    if edit:
        campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
        form = CampaignForm(obj=campaign)
        campaign_id = campaign.id
    else:
        campaign = Campaign()
        form = CampaignForm()
        campaign_id = None

    # for fields with dynamic choices, set to empty here in view
    # will be updated in client
    form.campaign_subtype.choices = choice_values_flat(CAMPAIGN_NESTED_CHOICES)
    form.target_set.choices = choice_items(EMPTY_CHOICES)

    # check request.form for campaign_subtype, reset if not present
    if not request.form.get('campaign_subtype'):
        form.campaign_subtype.data = None

    if form.validate_on_submit():
        # can't use populate_obj with nested forms, iterate over fields manually
        for field in form:
            if field.name != 'target_set':
                setattr(campaign, field.name, field.data)

        # handle target_set nested data
        target_list = []
        for target_data in form.target_set.data:
            # create Target object
            target = Target()
            for (field, val) in target_data.items():
                setattr(target, field, val)
            db.session.add(target)
            target_list.append(target)

            # update or create CampaignTarget membership
            try:
                campaign_target = CampaignTarget.query.filter_by(campaign=campaign, target=target).one()
            except sqlalchemy.orm.exc.NoResultFound:
                # create a new one
                campaign_target = CampaignTarget()
                campaign_target.campaign = campaign
                campaign_target.target = target
            # update order
            campaign_target.order = target_data['order']

            db.session.add(campaign_target)
            db.session.commit()

        # save campaign.target_set
        setattr(campaign, 'target_set', target_list)
        db.session.add(campaign)
        db.session.commit()

        if edit:
            flash('Campaign updated.', 'success')
        else:
            flash('Campaign created.', 'success')
        return redirect(url_for('campaign.audio', campaign_id=campaign.id))

    return render_template('campaign/form.html', form=form, edit=edit, campaign_id=campaign_id,
                           descriptions=current_app.config.CAMPAIGN_FIELD_DESCRIPTIONS,
                           CAMPAIGN_NESTED_CHOICES=CAMPAIGN_NESTED_CHOICES,
                           CUSTOM_CAMPAIGN_CHOICES=CUSTOM_CAMPAIGN_CHOICES)


@campaign.route('/<int:campaign_id>/copy', methods=['GET', 'POST'])
def copy(campaign_id):
    orig_campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
    new_campaign = orig_campaign.duplicate()

    db.session.add(new_campaign)
    db.session.commit()

    flash('Campaign copied.', 'success')
    return redirect(url_for('campaign.form', campaign_id=new_campaign.id))


@campaign.route('/<int:campaign_id>/audio', methods=['GET', 'POST'])
def audio(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
    form = CampaignAudioForm()

    if form.validate_on_submit():
        form.populate_obj(campaign)

        db.session.add(campaign)
        db.session.commit()

        flash('Campaign audio updated.', 'success')
        return redirect(url_for('campaign.launch', campaign_id=campaign.id))

    return render_template('campaign/audio.html', campaign=campaign, form=form,
                           descriptions=current_app.config.CAMPAIGN_FIELD_DESCRIPTIONS,
                           example_text=current_app.config.CAMPAIGN_MESSAGE_DEFAULTS)


@campaign.route('/<int:campaign_id>/audio/upload', methods=['POST'])
def upload_recording(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
    form = AudioRecordingForm()

    if form.validate_on_submit():
        message_key = form.data.get('key')

        # get highest version for this key to date
        last_version = db.session.query(db.func.max(AudioRecording.version)) \
            .filter_by(key=message_key) \
            .scalar()

        recording = AudioRecording()
        form.populate_obj(recording)
        recording.version = int(last_version or 0) + 1

        # save uploaded blob to file storage
        uploaded_blob = request.files.get('file_storage')
        if uploaded_blob:
            uploaded_blob.filename = "campaign_{}_{}_{}.mp3".format(campaign.id, message_key, recording.version)
            recording.file_storage = uploaded_blob
        db.session.add(recording)

        # unset selected for all other versions
        other_versions = CampaignAudioRecording.query.filter(
                            CampaignAudioRecording.campaign_id == campaign_id,
                            CampaignAudioRecording.recording.has(key=message_key)).all()
        for v in other_versions:
            v.selected = False
            db.session.add(v)
        db.session.commit()

        # link this recording to campaign through m2m, and set selected flag
        campaignRecording = CampaignAudioRecording(campaign_id=campaign.id, recording=recording)
        campaignRecording.selected = True
        
        db.session.add(campaignRecording)
        db.session.commit()

        message = "Audio recording uploaded"
        return jsonify({'success': True, 'message': message,
                        'key': message_key, 'version': recording.version})
    else:
        return jsonify({'success': False, 'errors': form.errors})


@campaign.route('/<int:campaign_id>/audio/<int:recording_id>/select', methods=['POST'])
def select_recording(campaign_id, recording_id):
    # ensure the requested ids exist
    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
    recording = AudioRecording.query.filter_by(id=recording_id).first_or_404()

    #unselect all other CampaignAudioRecordings with the same key and campaign
    other_versions = CampaignAudioRecording.query.filter(
                        CampaignAudioRecording.campaign_id == campaign_id,
                        CampaignAudioRecording.recording.has(key=recording.key)).all()
    for v in other_versions:
        v.selected = False
        db.session.add(v)
    db.session.commit()

    # select the requested recording
    campaignRecording = CampaignAudioRecording(campaign_id=campaign.id, recording=recording)
    campaignRecording.selected = True

    db.session.add(campaignRecording)
    db.session.commit()

    message = "Audio recording selected"
    return jsonify({'success': True, 'message': message,
                    'key': recording.key, 'version': recording.version})


@campaign.route('/<int:campaign_id>/audio/<int:recording_id>/delete', methods=['DELETE'])
def delete_recording(campaign_id, recording_id):
    recording = AudioRecording.query.filter_by(id=recording_id).first_or_404()
    campaignAudio = recording.campaign_audio_recordings.filter(campaign_id==campaign_id).all()

    # delete cascade for campaign audio recordings
    for car in campaignAudio:
        db.session.delete(car)
    db.session.delete(recording)
    db.session.flush()

    message = "Audio recording deleted"
    return jsonify({'success': True, 'message': message,
                    'key': recording.key, 'version': recording.version})


@campaign.route('/<int:campaign_id>/launch', methods=['GET', 'POST'])
def launch(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
    form = CampaignLaunchForm()

    if form.validate_on_submit():
        campaign.status = LIVE

        db.session.add(campaign)
        db.session.commit()

        flash('Campaign launched!', 'success')
        return redirect(url_for('campaign.index'))

    return render_template('campaign/launch.html', campaign=campaign, form=form)


@campaign.route('/<int:campaign_id>/status', methods=['GET', 'POST'])
def status(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
    form = CampaignStatusForm(obj=campaign)

    if form.validate_on_submit():
        form.populate_obj(campaign)

        db.session.add(campaign)
        db.session.commit()

        flash('Campaign status updated.', 'success')
        return redirect(url_for('campaign.index'))

    return render_template('campaign/status.html', campaign=campaign, form=form)
