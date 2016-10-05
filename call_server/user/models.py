from datetime import datetime

from sqlalchemy_utils.types import phone_number
from werkzeug import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

from ..extensions import db
from sqlalchemy import func
from .constants import (USER_ROLE, USER_ADMIN, USER_STAFF,
                        USER_STATUS, USER_ACTIVE,
                        STRING_LEN, PASSWORD_LEN_MAX)


class User(db.Model, UserMixin):
    __tablename__ = 'user_user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN), nullable=False, unique=True)
    email = db.Column(db.String(STRING_LEN), nullable=False, unique=True)
    openid = db.Column(db.String(STRING_LEN), unique=True)
    activation_key = db.Column(db.String(STRING_LEN))
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime)

    phone = db.Column(phone_number.PhoneNumberType())

    _password = db.Column('password', db.String(PASSWORD_LEN_MAX), nullable=False)

    def __unicode__(self):
        return self.name

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = generate_password_hash(password)
    # Hide password encryption by exposing password field only.
    password = db.synonym('_password',
                          descriptor=property(_get_password,
                                              _set_password))

    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password, password)

    # One-to-many relationship between users and roles.
    role_code = db.Column(db.SmallInteger, default=USER_STAFF)

    @property
    def role(self):
        return USER_ROLE[self.role_code]

    def is_admin(self):
        return self.role_code == USER_ADMIN

    # One-to-many relationship between users and user_statuses.
    status_code = db.Column(db.SmallInteger, default=USER_ACTIVE)

    @property
    def status(self):
        return USER_STATUS[self.status_code]

    # ================================================================
    # Class methods

    @classmethod
    def authenticate(cls, login, password):
        user = cls.query.filter(db.or_(
            func.lower(User.name) == func.lower(login),
            func.lower(User.email) == func.lower(login)
        )).first()

        if user:
            authenticated = user.check_password(password)
        else:
            authenticated = False

        return user, authenticated

    @classmethod
    def search(cls, keywords):
        criteria = []
        for keyword in keywords.split():
            keyword = '%' + keyword + '%'
            criteria.append(db.or_(
                User.name.ilike(keyword),
                User.email.ilike(keyword),
            ))
        q = reduce(db.and_, criteria)
        return cls.query.filter(q)

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first_or_404()

    def check_name(self, name):
        return User.query.filter(db.and_(User.name == name, User.email != self.id)).count() == 0
