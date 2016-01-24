"""
tests.py
"""
import os
import sys
import unittest

from google.appengine.ext import testbed
from google.appengine.ext import ndb
from appengine_fixture_loader.loader import load_fixture

from tweetdebate import app
from tweetdebate.views import tasks
from tweetdebate.models import Question
from tweetdebate.models import State

class AllTests(unittest.TestCase):
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

    def tearDown(self):
        self.testbed.deactivate()

    def test_view_tasks_twitter_post_status(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})

        result = tasks.__dict__["twitter_post_status"](1)
        assert "Posted new status" in result[0]
        assert result[1] == 200

        result = tasks.__dict__["twitter_post_status"](60*24*365*100)
        assert result[0] == "New question not ready"
        assert result[1] == 200

    def test_view_tasks_twitter_post_status_unstarted(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions_unstarted.json', 
                        kind={'Question': Question})

        # No last question so should always post something
        result = tasks.__dict__["twitter_post_status"](60*24*365*100)
        assert "Posted new status" in result[0]
        assert result[1] == 200

    def test_view_tasks_twitter_post_status_complete(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions_complete.json', 
                        kind={'Question': Question})

        # No last question so should always post something
        result = tasks.__dict__["twitter_post_status"](1)
        assert result[0] == "New question not ready"
        assert result[1] == 200

    def test_view_tasks_is_time_for_new_question(self):
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})
        
        # 1 minute cadence should be true
        result = tasks.__dict__["__is_time_for_new_question"](1)
        assert result == True

        # Should always be false for 100 years interval!
        result = tasks.__dict__["__is_time_for_new_question"](60*24*365*100)
        assert result == False
    
    def test_view_tasks_is_time_for_new_question_unstarted(self):
        load_fixture('tests/questions_unstarted.json', 
                        kind={'Question': Question})
        
        # 1 minute cadence should be true
        result = tasks.__dict__["__is_time_for_new_question"](1)
        assert result == True

        # Should always be false for 100 years interval!
        result = tasks.__dict__["__is_time_for_new_question"](60*24*365*100)
        assert result == True

    def test_model_state(self):
        # Load fixtures
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})

        question_entity = Question.get_current_question()
        State.update_state_scores(question_entity.state_scores)

        state_entity = State.get_state_by_abbreviation("CA")
        assert state_entity.party_score_votes[0] == 1
        assert state_entity.party_score_votes[1] == 0

        state_entity = State.get_state_by_abbreviation("WA")
        assert state_entity.party_score_votes[0] == 0
        assert state_entity.party_score_votes[1] == 1

        state_entity = State.get_state_by_abbreviation("NY")
        assert state_entity.party_score_votes[0] == 0
        assert state_entity.party_score_votes[1] == 0

    def test_model_question(self):
        # Load fixtures
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})

        # Check get next questions
        question_entity = Question.get_next_question()
        assert question_entity.key.id() == "q3"

        # Check get last question start  time
        current_question_start_time = Question.get_current_question_start_time()
        current_question_start_time_string = str(current_question_start_time)
        assert current_question_start_time_string == "2016-01-23 00:00:00"

    def test_model_question_unstarted(self):
        # Load fixtures
        load_fixture('tests/questions_unstarted.json', 
                        kind={'Question': Question})

        # Check get next questions
        question_entity = Question.get_next_question()
        assert question_entity.key.id() == "q1"

        # Check get current question start time
        current_question_start_time = Question.get_current_question_start_time()
        assert current_question_start_time == None

    def test_model_question_complete(self):
        # Load fixtures
        load_fixture('tests/questions_complete.json', 
                        kind={'Question': Question})

        # Check get next questions
        question_entity = Question.get_next_question()
        assert question_entity == None

        # Check get current question start  time
        current_question_start_time = Question.get_current_question_start_time()
        assert current_question_start_time == None

    def test_404(self):
        rv = self.app.get('/missing')
        assert rv.status == '404 NOT FOUND'
        assert 'Sorry, Nothing at this URL.' in rv.data

    
if __name__ == '__main__':
    unittest.main()