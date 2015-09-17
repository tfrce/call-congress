from uuid import uuid4
from datetime import datetime

from flask import (Blueprint, render_template, current_app, request,
                   flash, url_for, redirect, session, abort)
from flask.ext.mail import Message
from flask.ext.babel import gettext as _
from flask.ext.login import login_required, login_user, current_user, logout_user, confirm_login, login_fresh

from ..extensions import db, mail, login_manager

from .models import User
from .forms import (CreateUserForm, UserForm, UserRoleForm, LoginForm, ReauthForm,
    RecoverPasswordForm, ChangePasswordForm, InviteUserForm, RemoveUserForm)
from .constants import USER_NEW, USER_ACTIVE, USER_ADMIN
from .decorators import admin_required

user = Blueprint('user', __name__)


@user.route('/admin/user')
@login_required
@admin_required
def index():
    users = User.query.all()
    return render_template('user/list.html', users=users)


@user.route('/user/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('admin.dashboard'))

    form = LoginForm(login=request.args.get('login', None),
                     next=request.args.get('next', None))

    if form.validate_on_submit():
        user, authenticated = User.authenticate(form.login.data,
                                                form.password.data)

        if user and authenticated:
            remember = request.form.get('remember') == 'y'
            if login_user(user, remember=remember):
                flash(_("Logged in"), 'success')
            else:
                flash(_("Unable to log in"), 'warning')

            user.last_accessed = datetime.now()
            db.session.add(user)
            db.session.commit()

            return redirect(form.next.data or url_for('admin.dashboard'))
        else:
            flash(_('Sorry, invalid login'), 'warning')

    return render_template('user/login.html', form=form)


@user.route('/user/reauth', methods=['GET', 'POST'])
@login_required
def reauth():
    form = ReauthForm(next=request.args.get('next'))

    if request.method == 'POST':
        user, authenticated = User.authenticate(current_user.name,
                                                form.password.data)
        if user and authenticated:
            confirm_login()
            flash(_('Reauthenticated.'), 'success')
            return redirect(form.next.data or url_for('user.change_password'))

        flash(_('Password is incorrect.'), 'warning')
    return render_template('user/reauth.html', form=form)


@user.route('/user/logout')
@login_required
def logout():
    logout_user()
    flash(_('Logged out'), 'success')
    return redirect(url_for('site.index'))


@user.route('/user/create_account', methods=['GET', 'POST'])
def create_account():
    user = None
    if 'activation_key' in request.values and 'email' in request.values:
        activation_key = request.values['activation_key']
        email = request.values['email']
        user = User.query.filter_by(activation_key=activation_key) \
                         .filter_by(email=email).first()

    if user is None:
        return render_template('user/invalid_invitation.html',
            email=current_app.config['MAIL_DEFAULT_SENDER'], sitename=current_app.config['SITENAME'])

    form = CreateUserForm(obj=user)

    # can't use form.validate_on_submit, because username and email won't be unique
    if form.is_submitted() and form.validate_csrf_token(form):
        if form.password.validate(form) \
            and form.password_confirm.validate(form) \
                and form.phone.validate(form):

            # don't use populate_obj, which creates a new user, overwrite invidual fields instead
            user.email = form.email.data
            user.name = form.name.data
            user.password = form.password.data
            user.phone = form.phone.data
            user.status_code = USER_ACTIVE
            user.last_accessed = datetime.now()
            user.activation_key = None

            db.session.add(user)
            db.session.commit()

            if login_user(user):
                return redirect(form.next.data or url_for('admin.dashboard'))

    next = url_for('user.create_account', email=user.email, activation_key=user.activation_key)
    return render_template('user/create_account.html', next=next, form=form)


@user.route('/user/change_password', methods=['GET', 'POST'])
# not login_required, user auth'ed by activation_key
def change_password():
    user = None
    if current_user.is_authenticated():
        if not login_fresh():
            return login_manager.needs_refresh()
        user = current_user
    elif 'activation_key' in request.values and 'email' in request.values:
        activation_key = request.values['activation_key']
        email = request.values['email']
        user = User.query.filter_by(activation_key=activation_key) \
                         .filter_by(email=email).first()

    if user is None:
        abort(403)

    form = ChangePasswordForm(activation_key=user.activation_key)

    if form.validate_on_submit():
        user.password = form.password.data
        user.activation_key = None
        db.session.add(user)
        db.session.commit()

        flash(_("Your password has been changed, please log in again"),
              "success")
        return redirect(url_for("user.login"))

    return render_template("user/change_password.html", user=user, form=form)


@user.route('/user/reset_password', methods=['GET', 'POST'])
# not login_required, because user doesn't know password
def reset_password():
    form = RecoverPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            flash(_('Please check your email for instructions on how to access your account'), 'success')

            user.activation_key = str(uuid4())
            db.session.add(user)
            db.session.commit()

            url = url_for('user.change_password',
                email=user.email,
                activation_key=user.activation_key,
                _external=True)
            body = render_template('user/email/reset_password.txt',
                sitename=current_app.config['SITENAME'],
                username=user.name,
                url=url)
            message = Message(subject='Reset your password for ' + current_app.config['SITENAME'],
                body=body,
                recipients=[user.email])
            mail.send(message)

            return render_template('user/reset_password.html', form=form)
        else:
            flash(_('Sorry, no user found for that email address'), 'error')

    return render_template('user/reset_password.html', form=form)


@user.route('/user/profile', methods=['GET', 'POST'], defaults={'user_id': None})
@user.route('/user/<int:user_id>/profile', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if user_id:
        user = User.query.get(user_id)
    else:
        user = User.query.filter_by(email=current_user.email).first_or_404()

    form = UserForm(obj=user,
                    next=request.args.get('next'))

    if form.validate_on_submit():
        user.email = form.email.data
        user.name = form.name.data
        user.phone = form.phone.data

        db.session.add(user)
        db.session.commit()

        flash('User profile updated.', 'success')

    return render_template('user/profile.html', user=user, form=form)


@user.route('/user/invite', methods=['GET', 'POST'])
@login_required
@admin_required
def invite():
    form = InviteUserForm()

    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)

        user.activation_key = str(uuid4())
        user.status_code = USER_NEW
        user.password = user.activation_key  # reuse key until first login

        db.session.add(user)
        db.session.commit()

        url = url_for('user.create_account',
            email=user.email,
            activation_key=user.activation_key,
            _external=True)
        body = render_template('user/email/invite_user.txt', sitename=current_app.config['SITENAME'],
            username=user.name,
            url=url)
        message = Message(subject='Create account on ' + current_app.config['SITENAME'],
            body=body,
            recipients=[user.email])
        mail.send(message)

        flash(_('Invited ' + user.email), 'success')
        return redirect(url_for('user.index'))

    return render_template('user/invite.html', form=form)


@user.route('/admin/user/<int:user_id>/role', methods=['GET', 'POST'])
@login_required
@admin_required
def role(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    form = UserRoleForm(obj=user, next=request.args.get('next'))

    if form.validate_on_submit():
        if ((user == current_user)
        and (user.role_code is USER_ADMIN)
        and (int(form.data['role_code']) > 0)):
            flash("Cannot remove your own admin role.", 'warning')
            return render_template('user/role.html', user=user, form=form)
        else:
            form.populate_obj(user)
            db.session.add(user)
            db.session.commit()

            flash('User role updated.', 'success')
        return redirect(url_for('user.index'))

    return render_template('user/role.html', user=user, form=form)


@user.route('/user/<int:user_id>/remove', methods=['GET', 'POST'])
@login_required
@admin_required
def remove(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()

    if user == current_user:
        flash('Cannot remove yourself.', 'warning')
        return redirect(url_for('user.index'))

    form = RemoveUserForm(obj=user, username=user.name)

    if form.validate_on_submit():
        db.session.delete(user)
        db.session.commit()

        flash('User removed.', 'success')
        return redirect(url_for('user.index'))

    return render_template('user/remove.html', user=user, form=form)


@user.route('/user/lang/', methods=['POST'])
def lang():
    session['language'] = request.form['language']
    new_language = current_app.config['ACCEPT_LANGUAGES'][request.form['language']]
    flash(_('Language changed to ') + new_language, 'success')
    return redirect(url_for('admin.dashboard'))
