import datetime
import time
import logging

from flask import Blueprint
from tweetdebate.models import GameStatus
from tweetdebate.models import Question
from tweetdebate.models import Vote
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
        return 'No game status', 200

    question_cadence_minutes = game_status.question_cadence_minutes
    last_question_start_time = game_status.last_question_start_time
    next_question_start_time = last_question_start_time + \
        datetime.timedelta(minutes=question_cadence_minutes)

    # If last question was asked too far in the past
    if datetime.datetime.now() > next_question_start_time:
        question_entity = Question.get_next_question()
        if question_entity is None:
            return 'Out of questions', 200
        
        question_text = question_entity.question_text
        question_entity.start_time = datetime.datetime.now()

        #twitter_api = TwitterAPI()
        #twitter_api.update_status(question_text)

        if game_status.current_question is not None:
            game_status.current_question.end_time = datetime.datetime.now()
            self.__updateStateScore(question_entity)

        # @TODO assumes that Twitter post is always successful
        game_status.current_question = question_entity
        game_status.posted_question_count += 1
        game_status.last_question_start_time = datetime.datetime.now()
        game_status.put()
        return 'Posted new status [%s]' % question_text, 200

    return 'Status not ready to post', 200

def __updateStateScore(question_entity):
    votes = Vote.query_by_question(question_entity)
    state_votes = {}

    # Tally individual votes for all states
    if votes not None:
        for vote in votes:
            if vote.state not in state_scores:
                state_votes[vote.state] = {"score_democrat": 0,
                                           "score_republican": 0}
            if question_entity.democrat:
                state_votes[vote.state]["democrat"] +=1
            else:
                state_votes[vote.state]["republican"] +=1

    # Update state scores
    for key, value in state_votes:
        state_score_entity = StateScore.get_state_score(key)
        if value["score_democrat"] == value["score_republican"]:
            # Draw adds score of one to each side for a state
            ++state_score_entity.score_democrat
            ++state_score_entity.score_republican
        else if value["score_democrat"] > value["score_republican"]:
            ++state_score_entity.score_democrat
        else:
            ++state_score_entity.score_republican

        # Update state score
        state_score_entity.put()

@mod.route("/tasks/twitter_stream")
def twitter_stream():
    """ Check if Twitter Stream task is running.
    If not, restart it.
    """
    twitter_stream = TwitterStream()
    if not twitter_stream.is_running():
      twitter_stream.start()

    return 'Actvated Twitter Stream', 200
