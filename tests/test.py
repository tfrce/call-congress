import os
import flaskr
import unittest
import tempfile

from call_server.extensions import assets


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        self.app = flaskr.app.test_client()
        flaskr.init_db()

        # clear assets
        assets._named_bundles = {}

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])


if __name__ == '__main__':
    unittest.main()
