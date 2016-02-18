import endpoints
import webtest

from appengine_fixture_loader.loader import load_fixture
from test_base import TestBase

from tweetdebate.models import Question
from tweetdebate.models import State

class TestAPI(TestBase):
    def setUp(self):
        return super(TestAPI, self).setUp()

    def tearDown(self):
        self.testbed.deactivate()

    def test_api_question(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})
        response = self.app.get('/api/questions')