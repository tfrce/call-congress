import nose
from flask.ext.testing import TestCase

from call_server.app import create_app, db
from call_server.config import TestingConfig
from call_server.extensions import assets


class BaseTestCase(TestCase):

    def create_app(self):
        assets._named_bundles = {}
        return create_app(TestingConfig)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

if __name__ == '__main__':
    nose.main()
