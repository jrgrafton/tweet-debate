import datetime
import time
import logging

from flask import Blueprint
from tweetdebate.models import GameStatus
from tweetdebate.models import Question
from tweetdebate.tasks.twitter_api import TwitterAPI
from tweetdebate.tasks.twitter_stream import TwitterStream

mod = Blueprint('tasks', __name__)

@mod.route("/tasks/twitter_post_status")
def twitter_post_status():
    """ Potentially post a new status to Twitter
    """
    # Check if it's time to post
    game_status = GameStatus.get_game_status()
    if game_status is None:
        return 'No game status', 500

    question_cadence_minutes = game_status.question_cadence_minutes
    last_question_start_time = game_status.last_question_start_time
    next_question_start_time = last_question_start_time + \
        datetime.timedelta(minutes=question_cadence_minutes)

    # If last question was asked too far in the past
    if datetime.datetime.now() > next_question_start_time:
        question = Question.get_next_question()
        if question is None:
            return 'Out of questions', 500
        
        question_id = question.key.id()
        question_text = question.question_text
        next_state = GameStatus.get_next_state()

        question_text = "%s %s governor wants to know!" % \
                        (question_text, next_state["abbreviation"])

        #twitter_api = TwitterAPI()
        #twitter_api.update_status(question_text)

        #if game_status.current_question_id is not None:
        # @TODO update StateScore for last question
        # @TODO update History

        # @TODO assumes that post is always successful
        # game_status.current_question_id = question_id
        # game_status.posted_question_count += 1
        # game_status.last_question_start_time = datetime.datetime.now()
        # game_status.put()
        return 'Posted new status [%s]' % question_text, 200

    return 'Status not ready to post', 200

@mod.route("/tasks/twitter_stream")
def twitter_stream():
    """ Check if Twitter Stream task is running.
    If not, restart it.
    """
    twitter_stream = TwitterStream()
    if not twitter_stream.is_running():
      twitter_stream.start()

    return 'Actvated Twitter Stream', 200
