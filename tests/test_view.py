"""
test_views.py - tests views
"""
import json
import os

from flask.ext.api import status
from google.appengine.ext import ndb
from appengine_fixture_loader.loader import load_fixture

from tweetdebate.models import Question
from tweetdebate.models import State
from tweetdebate.models import User
from tweetdebate.views import tasks
from tweetdebate.views.tasks import TwitterStreamListener
from tweetdebate.tasks.twitter_api import TwitterAPI
from test_base import TestBase

class TestView(TestBase):
    def setUp(self):
        return super(TestView, self).setUp()

    def tearDown(self):
        self.testbed.deactivate()

    """def test_view_tasks_twitter_stream(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})

        reponse = \
            self.app.get('/tasks/twitter_stream?action=start')
        assert "Started Twitter Stream" in reponse.data
        
        # TODO: check for PID file
        # TODO: activate again and ensure no crash
        # TODO: call stop and check for removal of PID file
"""
   
    def test_view_tasks_twitter_stream_listener_get_party(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions_no_votes.json', 
                        kind={'Question': Question,'State': State})

        twitter_stream_listener = TwitterStreamListener()

        # party from string extraction
        current_question = Question.get_current_question()
        current_question_party = current_question.party

        test_text = "#NO #no I disagree"
        result = twitter_stream_listener. \
            get_party_from_string_using_question(test_text, current_question)
        assert result == 1 - current_question_party # Inverse current party

        test_text = "#YeS I agree"
        result = twitter_stream_listener. \
            get_party_from_string_using_question(test_text, current_question)
        assert result == current_question_party 

        test_text = "#YeSssir I agree"
        result = twitter_stream_listener. \
            get_party_from_string_using_question(test_text, current_question)
        assert result == None

        test_text = "#nobody agree(s)"
        result = twitter_stream_listener. \
            get_party_from_string_using_question(test_text, current_question)
        assert result == None

        test_text = "NO no I disagree"
        result = twitter_stream_listener. \
            get_party_from_string_using_question(test_text, current_question)
        assert result == None

        test_text = "#Yes #Yes #no I agree"
        result = twitter_stream_listener. \
            get_party_from_string_using_question(test_text, current_question)
        assert result == None

    def test_view_tasks_twitter_stream_listener_get_state(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions_no_votes.json', 
                        kind={'Question': Question,'State': State})

        twitter_stream_listener = TwitterStreamListener()

        test_text = "#AL #no I agree"
        result = twitter_stream_listener.get_state_from_string(test_text)
        assert result == "AL"

        test_text = "#ALAL #no I agree"
        result = twitter_stream_listener.get_state_from_string(test_text)
        assert result == None

        test_text = "AL #no I agree"
        result = twitter_stream_listener.get_state_from_string(test_text)
        assert result == None

        test_text = "#AL #AK #no I agree"
        result = twitter_stream_listener.get_state_from_string(test_text)
        assert result == None

        test_text = "#no I agree"
        result = twitter_stream_listener.get_state_from_string(test_text)
        assert result == None

    def test_view_tasks_twitter_stream_listener_on_data(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions_no_votes.json', 
                        kind={'Question': Question,'State': State})

        twitter_stream = open(os.path.join(os.path.dirname(__file__),
                                          'twitter_stream.json'))
        twitter_stream = json.load(twitter_stream)

        twitter_stream_listener = TwitterStreamListener()
        twitter_stream_listener.on_data(twitter_stream["twitter_reply_old"])
        users = User.get_all()
        assert len(users) == 0

        twitter_stream_listener.on_data(
            twitter_stream["twitter_reply_old"])
        users = User.get_all()
        assert len(users) == 0
        
        twitter_stream_listener.on_data(
            twitter_stream["twitter_reply_current_invalid"])
        users = User.get_all()
        assert len(users) == 0
        
        twitter_stream_listener.on_data(
            twitter_stream["twitter_post"])
        users = User.get_all()
        assert len(users) == 0
        
        twitter_stream_listener.on_data(
            twitter_stream["twitter_mention"])
        users = User.get_all()
        assert len(users) == 0

        twitter_stream_listener.on_data(
            twitter_stream["twitter_retweet"])
        users = User.get_all()
        assert len(users) == 0

        twitter_stream_listener.on_data(
            twitter_stream["twitter_favourite"])
        users = User.get_all()
        assert len(users) == 0

        twitter_stream_listener.on_data(
            twitter_stream["twitter_favourite_reply"])
        users = User.get_all()
        assert len(users) == 0

        current_question = Question.get_current_question()
        assert len(current_question.state_scores) == 0

        twitter_stream_listener.on_data(
            twitter_stream["twitter_reply_current_valid_user1"])
        users = User.get_all()
        assert len(users) == 1

        current_question = Question.get_current_question()
        assert len(current_question.state_scores) == 1
        assert current_question.state_scores[0].state_abbreviation == "CA"
        assert current_question.state_scores[0].party_score_votes[0] == 0
        assert current_question.state_scores[0].party_score_votes[1] == 1

        twitter_stream_listener.on_data(
            twitter_stream["twitter_reply_current_valid_user1"])
        users = User.get_all()
        assert len(users) == 1
        assert len(users[0].votes) == 1
        current_question = Question.get_current_question()
        assert len(current_question.state_scores) == 1
        assert current_question.state_scores[0].state_abbreviation == "CA"
        assert current_question.state_scores[0].party_score_votes[0] == 0
        assert current_question.state_scores[0].party_score_votes[1] == 1

        twitter_stream_listener.on_data(
            twitter_stream["twitter_reply_current_valid_user2"])
        users = User.get_all()
        assert len(users) == 2
        current_question = Question.get_current_question()
        assert len(current_question.state_scores) == 2
        assert current_question.state_scores[1].state_abbreviation == "WA"
        assert current_question.state_scores[1].party_score_votes[0] == 1
        assert current_question.state_scores[1].party_score_votes[1] == 0

        twitter_stream_listener.on_data(
            twitter_stream["twitter_reply_current_valid_user2"])
        users = User.get_all()
        assert len(users) == 2

        # TODO: Verify Question.state_scores

    def test_view_tasks_twitter_post_status(self):
        # TODO: allow for twitter based tests when done with others 
        return;

        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})

        # Delete all previous tweets before proceeding
        twitter_api = TwitterAPI()
        twitter_api.delete_all_tweets()

        reponse = \
            self.app.get('/tasks/twitter_post_status' \
                '?question_cadence_minutes=1&post_to_twitter=True')
        current_question = Question.get_current_question()
        ndb.get_context().clear_cache()
        assert current_question.twitterid != None
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
