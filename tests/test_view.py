"""
test_views.py - tests views
"""
from threading import Thread
import json
import os
import sys
import time

from flask.ext.api import status
from google.appengine.ext import ndb
from appengine_fixture_loader.loader import load_fixture

from tweetdebate.models import Question
from tweetdebate.models import State
from tweetdebate.models import User
from tweetdebate.models import Vote
from tweetdebate.views import backend
from tweetdebate.views import tasks
from tweetdebate.views.tasks import sway_points
from tweetdebate.views.backend import TwitterStreamListener
from tweetdebate.tasks.twitter_api import TwitterAPI
from test_base import TestBase

class TestView(TestBase):
    def setUp(self):
        return super(TestView, self).setUp()

    def tearDown(self):
        self.testbed.deactivate()

    def _start_twitter_stream(self):
        backend.start_twitter_stream()

    def test_view_tasks_twitter_stream(self):
        if os.getenv('TWITTER_TESTS') == "FALSE":
            return # Modify in runtests.sh

        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})

        # Start new thread with Twitter Stream listener
        stream_thread = Thread(target=self._start_twitter_stream)
        stream_thread.daemon = True
        stream_thread.start()

        # Delete all previous tweets before proceeding
        twitter_api = TwitterAPI()
        twitter_api.delete_all_tweets()

        reponse = \
            self.app.get('/tasks/twitter_post_status' \
                '?question_cadence_minutes=1&post_to_twitter=True')
        current_question = Question.get_current_question()

        # Post reply
        twitter_status_id = twitter_api.get_last_tweet().id
        twitter_api.update_status("#yes for #WA", twitter_status_id)

        # Wait for stream to be updated
        time.sleep(2)

        # Test to see reply has been registered
        ndb.get_context().clear_cache()
        users = User.get_all()
        assert len(users) == 1

        current_question = Question.get_current_question()
        assert len(current_question.state_scores) == 1
        assert current_question.state_scores[0].state_abbreviation == "WA"
        assert current_question.state_scores[0].party_score_votes[0] == 1
        assert current_question.state_scores[0].party_score_votes[1] == 0

    # Also covers parse_data
    def test_view_tasks_twitter_stream_listener_on_data(self):
        return

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
        assert current_question.state_scores[0].party_score_sway[0] == 0
        assert current_question.state_scores[0].party_score_sway[0] == 50
        assert users[0].sway_points == 0

        twitter_stream_listener.on_data(
            twitter_stream["twitter_reply_current_valid_user1"])
        users = User.get_all()
        assert len(users) == 1
        assert len(users[0].votes) == 1
        assert users[0].sway_points == 50

        current_question = Question.get_current_question()
        assert len(current_question.state_scores) == 1
        assert current_question.state_scores[0].state_abbreviation == "CA"
        assert current_question.state_scores[0].party_score_votes[0] == 0
        assert current_question.state_scores[0].party_score_votes[1] == 1
        assert current_question.state_scores[0].party_score_sway[0] == 0
        assert current_question.state_scores[0].party_score_sway[0] == 50
        assert users[0].sway_points == 0

        twitter_stream_listener.on_data(
            twitter_stream["twitter_reply_current_valid_user2"])
        users = User.get_all()
        assert len(users) == 2
        current_question = Question.get_current_question()
        assert len(current_question.state_scores) == 2
        assert current_question.state_scores[1].state_abbreviation == "WA"
        assert current_question.state_scores[1].party_score_votes[0] == 1
        assert current_question.state_scores[1].party_score_votes[1] == 0
        assert current_question.state_scores[1].party_score_votes[0] == 20
        assert current_question.state_scores[1].party_score_votes[1] == 0
        assert users[1].sway_points == 30

        twitter_stream_listener.on_data(
            twitter_stream["twitter_reply_current_valid_user2"])
        users = User.get_all()
        assert len(users) == 2

    def test_view_tasks_twitter_stream_listener_add_vote_for_screenname(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})
        twitter_stream_listener = TwitterStreamListener()
        current_question = Question.get_current_question()
        
        result = twitter_stream_listener.\
                    add_vote_for_screenname(current_question,
                                            "123",
                                            None, # Invalid state
                                            1,
                                            0,
                                            "jrgrafton")
        assert result == False

        result = twitter_stream_listener.\
            add_vote_for_screenname(current_question,
                                    "123",
                                    "CA",
                                    None, # Invalid party
                                    0,
                                    "jrgrafton")
        assert result == False

        # First valid user
        result = twitter_stream_listener.\
            add_vote_for_screenname(current_question,
                                    "123",
                                    "CA",
                                    0,
                                    100,
                                    "jrgrafton")
        assert result == True
        user = User.query_by_userid("jrgrafton").get()
        assert user != None
        assert len(user.votes) == 1
        assert user.votes[0].question.get().key == current_question.key
        assert user.votes[0].replyid == "123"
        assert user.votes[0].state_abbreviation == "CA"
        assert user.votes[0].party == 0
        assert user.votes[0].sway_points == 100

        # Second vote for user on same question
        result = twitter_stream_listener.\
            add_vote_for_screenname(current_question,
                                    "123",
                                    "WA",
                                    1,
                                    0,
                                    "jrgrafton")
        assert result == False

        # Second valid user
        result = twitter_stream_listener.\
            add_vote_for_screenname(current_question,
                                    "123",
                                    "WA",
                                    1,
                                    50,
                                    "jrgrafton_test")
        assert result == True
        users = User.get_all()
        assert len(users) == 2
        user = users[1]
        assert len(user.votes) == 1
        assert user.votes[0].question.get().key == current_question.key
        assert user.votes[0].replyid == "123"
        assert user.votes[0].state_abbreviation == "WA"
        assert user.votes[0].party == 1
        assert user.votes[0].sway_points == 50

        # Go to new question and test valid votes
        reponse = self.app.get('/tasks/twitter_post_status' \
                               '?question_cadence_minutes=1')
        current_question = Question.get_current_question()

        # Second vote for new question should work
        result = twitter_stream_listener.\
            add_vote_for_screenname(current_question,
                                    "124",
                                    "WA",
                                    1,
                                    10,
                                    "jrgrafton")
        assert result == True
        user = User.query_by_userid("jrgrafton").get()
        assert user != None
        assert len(user.votes) == 2
        assert user.votes[1].question.get().key == current_question.key
        assert user.votes[1].replyid == "124"
        assert user.votes[1].state_abbreviation == "WA"
        assert user.votes[1].party == 1
        assert user.votes[1].sway_points == 10


    def test_view_tasks_twitter_stream_listener_add_vote_for_question(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions_no_votes.json', 
                        kind={'Question': Question,'State': State})
        
        current_question = Question.get_current_question()
        assert len(current_question.state_scores) == 0

        twitter_stream_listener = TwitterStreamListener()
        twitter_stream_listener.add_vote_for_question(0,
                                                      30,
                                                      "CA",
                                                      current_question)

        current_question = Question.get_current_question()
        assert len(current_question.state_scores) == 1
        assert current_question.state_scores[0].state_abbreviation == "CA"
        assert current_question.state_scores[0].party_score_votes[0] == 1
        assert current_question.state_scores[0].party_score_votes[1] == 0
        assert current_question.state_scores[0].party_score_sway[0] == 30
        assert current_question.state_scores[0].party_score_sway[1] == 0

        twitter_stream_listener.add_vote_for_question(0,
                                                      50,
                                                      "CA",
                                                      current_question)
        twitter_stream_listener.add_vote_for_question(1,
                                                      20,
                                                      "CA",
                                                      current_question)
        assert current_question.state_scores[0].party_score_votes[0] == 2
        assert current_question.state_scores[0].party_score_votes[1] == 1
        assert current_question.state_scores[0].party_score_sway[0] == 80
        assert current_question.state_scores[0].party_score_sway[1] == 20

        twitter_stream_listener.add_vote_for_question(1,
                                                      30,
                                                      "WA",
                                                      current_question)
        assert len(current_question.state_scores) == 2
        assert current_question.state_scores[1].state_abbreviation == "WA"
        assert current_question.state_scores[1].party_score_votes[0] == 0
        assert current_question.state_scores[1].party_score_votes[1] == 1
        assert current_question.state_scores[1].party_score_sway[0] == 0
        assert current_question.state_scores[1].party_score_sway[1] == 30

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

        test_text = "I disagree #no"
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

        test_text = "#no I agree #AL"
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

    def test_view_tasks_twitter_stream_listener_get_sway(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions_no_votes.json', 
                        kind={'Question': Question,'State': State})

        twitter_stream_listener = TwitterStreamListener()

        test_text = "#SWAY20 #SWAY10"
        result = twitter_stream_listener.get_sway_from_string(test_text)
        assert result == 0

        test_text = "NO #SWAY MAN"
        result = twitter_stream_listener.get_sway_from_string(test_text)
        assert result == 0

        test_text = "NO SWAY MAN"
        result = twitter_stream_listener.get_sway_from_string(test_text)
        assert result == 0

        test_text = "NO #SWAY20 #SWAY MAN"
        result = twitter_stream_listener.get_sway_from_string(test_text)
        assert result == 0

        test_text = "#SWAY2 Testing"
        result = twitter_stream_listener.get_sway_from_string(test_text)
        assert result == 2

        test_text = "Testing #SWAY200"
        result = twitter_stream_listener.get_sway_from_string(test_text)
        assert result == 200

    def test_view_tasks_twitter_post_status(self):
        if os.getenv('TWITTER_TESTS') == "FALSE":
            return # Modify in runtests.sh

        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})
        current_question = Question.get_current_question()

        # Add user with vote so we can test sway points
        vote_current = Vote(
            question = current_question.key,
            replyid = "123",
            state_abbreviation = "CA",
            party = 0,
            sway_points = 20
        )
        user = User(
            userid = "jrgrafton",
            votes = [vote_current],
            # Used 20 sway points upon creation
            sway_points = 30
        )
        user.put()

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
        twitter_status = twitter_api.get_last_tweet().text
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

    def test_view_tasks_attribute_sway_points_for_user(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})
        current_question = Question.get_current_question()
        vote_previous = Vote(
            question = current_question.key,
            replyid = "123",
            state_abbreviation = "CA",
            party = 0,
            sway_points = 20,
            winning_vote = True
        )
        vote_current = Vote(
            question = current_question.key,
            replyid = "123",
            state_abbreviation = "CA",
            party = 0,
            sway_points = 20,
            winning_vote = None
        )
        user = User(
            userid = "jrgrafton",
            votes = [vote_current],
            # Can use sway points upon creation
            sway_points = 30
        )

        # So that we can determine if user had winning vote
        State.update_state_scores(current_question.state_scores)

        # Vote - loosing (party 0 has least votes for this question and state)
        original_sway_points = user.sway_points
        tasks.__dict__\
            ["__attribute_sway_points_for_user"](current_question, user)

        assert user.sway_points == original_sway_points + \
                                   sway_points["submit_answer"]

        # Vote - winning (party 1 has most votes for this question and state)
        original_sway_points = user.sway_points
        vote_current.party = 1
        tasks.__dict__\
            ["__attribute_sway_points_for_user"](current_question, user)
        assert user.sway_points == original_sway_points + \
                                  sway_points["submit_answer"] + \
                                  sway_points["submit_winning_answer"] + \
                                  int(vote_current.sway_points * \
                                      sway_points["refund"])

        # Vote - winning + streak
        original_sway_points = user.sway_points
        user.votes.insert(0, vote_previous)
        tasks.__dict__\
            ["__attribute_sway_points_for_user"](current_question, user)
        assert user.sway_points == original_sway_points + \
                                  sway_points["submit_answer"] + \
                                  sway_points["submit_winning_answer"] + \
                                  sway_points["streak_bonus"] + \
                                  int(vote_current.sway_points * \
                                      sway_points["refund"])

    def test_404(self):
        result = self.app.get('/missing')
        assert result.status == '404 NOT FOUND'
        assert 'Sorry, Nothing at this URL.' in result.data
