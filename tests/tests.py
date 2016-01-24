#!/usr/bin/env python
# encoding: utf-8
"""
tests.py
"""
import os
import unittest

from google.appengine.ext import testbed
from google.appengine.ext import ndb
from appengine_fixture_loader.loader import load_fixture

from tweetdebate import app
from tweetdebate.models import Vote

class DemoTestCase(unittest.TestCase):
    def setUp(self):
        # Flask apps testing. See: http://flask.pocoo.org/docs/testing/
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        self.app = app.test_client()

        # Setups app engine test bed. See: http://goo.gl/eQWKdr
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.testbed.init_memcache_stub()

        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

        # Load fixtures
        loaded_data = load_fixture('tests/questions.json', kind = Question)

    def tearDown(self):
        self.testbed.deactivate()

    def test_404(self):
        rv = self.app.get('/missing')
        assert rv.status == '404 NOT FOUND'
        assert 'Sorry, Nothing at this URL.' in rv.data

    
if __name__ == '__main__':
    unittest.main()