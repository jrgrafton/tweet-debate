import datetime
import time
import logging

from flask import Blueprint
from flask import request
from tweetdebate.models import Question
from tweetdebate.models import State
from tweetdebate.tasks.twitter_api import TwitterAPI
from tweetdebate.tasks.twitter_stream import TwitterStream

mod = Blueprint('tasks', __name__)

@mod.route("/tasks/twitter_post_status")
def twitter_post_status():
    """ Potentially post a new status to Twitter
    """
    # Can be overriden in GET request
    question_cadence_minutes = \
        int(request.args.get('question_cadence_minutes', 60 * 6))
    post_to_twitter = request.args.get('post_to_twitter', False)
    
    next_question = Question.get_next_question()
    if next_question is not None \
            and __is_time_for_new_question(question_cadence_minutes):
        current_question = Question.get_current_question()
        
        #TODO: detect Twitter failures - add to monitoring and log files?
        if post_to_twitter != False:
            twitter_api = TwitterAPI()
            twitter_api.update_status(next_question.question_text)

        if current_question is not None:
            current_question.end_time = datetime.datetime.now()
            current_question.put()
            State.update_state_scores(current_question.state_scores)
        
        next_question.start_time = datetime.datetime.now()
        next_question.put()

        return 'Posted new status [%s]' % next_question.question_text, 200

    return 'New question not ready', 200

def __is_time_for_new_question(question_cadence_minutes):
    current_question = Question.get_current_question()
    if current_question == None:
        return True
    else:
        question_start_time = current_question.start_time
        next_question_start_time = question_start_time + \
            datetime.timedelta(minutes=question_cadence_minutes)
        return datetime.datetime.now() > next_question_start_time

@mod.route("/tasks/twitter_stream")
def twitter_stream():
    """ Check if Twitter Stream task is running.
    If not, restart it.
    """
    twitter_stream = TwitterStream()
    if not twitter_stream.is_running():
      twitter_stream.start()

    return 'Actvated Twitter Stream', 200
