"""
test_views.py - tests views
"""
from flask.ext.api import status
from appengine_fixture_loader.loader import load_fixture

from tweetdebate.models import Question
from tweetdebate.models import State
from tweetdebate.views import tasks
from tweetdebate.tasks.twitter_api import TwitterAPI
from test_base import TestBase

class TestView(TestBase):
    def setUp(self):
        return super(TestView, self).setUp()

    def tearDown(self):
        self.testbed.deactivate()

    def test_view_tasks_twitter_post_status(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})

        # Delete all previous tweets before proceeding
        twitter_api = TwitterAPI()
        twitter_api.delete_all_tweets()

        reponse = \
            self.app.get('/tasks/twitter_post_status' \
                '?question_cadence_minutes=1&post_to_twitter=True')
        assert "Posted new status" in reponse.data
        assert status.is_success(reponse.status_code) == True

        # Ensure Twitter timeline has been updated
        twitter_status = twitter_api.get_last_tweet()
        question_entity = Question.get_current_question()
        assert twitter_status == question_entity.question_text

        # Expect question not to be posted as time is not yet up
        reponse = \
            self.app.get('/tasks/twitter_post_status' \
                '?question_cadence_minutes=52560000')
        assert "New question not ready" in reponse.data
        assert status.is_success(reponse.status_code) == True

    def test_view_tasks_twitter_post_status_unstarted(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions_unstarted.json', 
                        kind={'Question': Question})

        # No last question so should always post something
        # Doesn't post to Twitter - we don't want to overload the API
        reponse = \
            self.app.get('/tasks/twitter_post_status' \
                '?question_cadence_minutes=52560000')
        assert "Posted new status" in reponse.data
        assert status.is_success(reponse.status_code) == True

    def test_view_tasks_twitter_post_status_complete(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions_complete.json', 
                        kind={'Question': Question})

        # No more questions so should never post anything
        # Doesn't post to Twitter - we don't want to overload the API
        reponse = \
            self.app.get('/tasks/twitter_post_status' \
                '?question_cadence_minutes=1')
        assert "New question not ready" in reponse.data
        assert status.is_success(reponse.status_code) == True

    def test_view_tasks_is_time_for_new_question(self):
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})
        
        # 1 minute cadence should be true
        result = tasks.__dict__["__is_time_for_new_question"](1)
        assert result == True

        # Should always be false for 100 years interval!
        result = \
            tasks.__dict__["__is_time_for_new_question"](60*24*365*100)
        assert result == False
    
    def test_view_tasks_is_time_for_new_question_unstarted(self):
        load_fixture('tests/questions_unstarted.json', 
                        kind={'Question': Question})
        
        # 1 minute cadence should be true
        result = tasks.__dict__["__is_time_for_new_question"](1)
        assert result == True

        # Should always be false for 100 years interval!
        result = \
            tasks.__dict__["__is_time_for_new_question"](60*24*365*100)
        assert result == True

    def test_404(self):
        result = self.app.get('/missing')
        assert result.status == '404 NOT FOUND'
        assert 'Sorry, Nothing at this URL.' in result.data
