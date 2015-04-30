# -*- coding: utf-8 -*-

from flask import Markup

from flask.ext.wtf import Form
from flask.ext.babel import gettext as _
from wtforms import (HiddenField, BooleanField, TextField,
                     PasswordField, SubmitField,
                     RadioField, DateField)
from wtforms.validators import ValidationError, Required, Length, EqualTo, Email, AnyOf
from flask_wtf.html5 import EmailField

from .models import User
from .constants import (PASSWORD_LEN_MIN, PASSWORD_LEN_MAX,
                        USERNAME_LEN_MIN, USERNAME_LEN_MAX,
                        USER_ROLE, USER_STATUS)


class LoginForm(Form):
    next = HiddenField()
    login = TextField(_('Username or email'), [Required()])
    password = PasswordField(_('Password'), [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    remember = BooleanField(_('Remember me'))
    submit = SubmitField(_('Sign in'))


class UserForm(Form):
    next = HiddenField()
    role_code = RadioField(_("Role"), [AnyOf([str(val) for val in USER_ROLE.keys()])],
                           choices=[(str(val), label) for val, label in USER_ROLE.items()])
    status_code = RadioField(_("Status"), [AnyOf([str(val) for val in USER_STATUS.keys()])],
                             choices=[(str(val), label) for val, label in USER_STATUS.items()])
    # A demo of datepicker.
    created_time = DateField(_('Created time'))
    submit = SubmitField(_('Save'))


class SignupForm(Form):
    next = HiddenField()
    email = EmailField(_('Email'), [Required(), Email()],
                       description=_("What's your email address?"))
    password = PasswordField(_('Password'), [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)],
                             description=_('%s characters or more' % PASSWORD_LEN_MIN))
    name = TextField(_('Choose your username'), [Required(), Length(USERNAME_LEN_MIN, USERNAME_LEN_MAX)],
                     description=_("Don't worry. you can change it later."))
    submit = SubmitField(_('Sign up'))

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first() is not None:
            raise ValidationError(_('This username is already registered'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError(_('This email is already registered'))


class RecoverPasswordForm(Form):
    email = EmailField(_('Your email'), [Email()])
    submit = SubmitField(_('Send instructions'))


class ChangePasswordForm(Form):
    activation_key = HiddenField()
    password = PasswordField(u'Password', [Required()])
    password_again = PasswordField(u'Password again', [EqualTo('password', message="Passwords don't match")])
    submit = SubmitField('Save')


class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField(u'Password', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    submit = SubmitField('Reauthenticate')


class CreateProfileForm(Form):
    openid = HiddenField()
    name = TextField(u'Choose your username', [Required(), Length(USERNAME_LEN_MIN, USERNAME_LEN_MAX)],
                     description=u"Don't worry. you can change it later.")
    email = EmailField(u'Email', [Required(), Email()], description=u"What's your email address?")
    password = PasswordField(u'Password', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)],
                             description=u'%s characters or more! Be tricky.' % PASSWORD_LEN_MIN)
    submit = SubmitField(u'Create Profile')

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first() is not None:
            raise ValidationError(u'This username is taken.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError(u'This email is taken.')
