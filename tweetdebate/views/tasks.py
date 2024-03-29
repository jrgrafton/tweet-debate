import datetime
import logging
import re

from flask import Blueprint
from flask import request
from tweetdebate.models import Question
from tweetdebate.models import State
from tweetdebate.models import User
from tweetdebate.tasks.twitter_api import TwitterAPI
from tweetdebate.tasks.twitter_stream import TwitterStream
from tweepy import TweepError

mod = Blueprint('tasks', __name__)
sway_points = {
    "submit_answer" : 1,
    "submit_winning_answer" : 1,
    "streak_bonus" : 1,
    "refund" : 0.25 # % of sway points refunded on correct vote 
}

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
        
        if post_to_twitter != False:
            try:
                twitter_api = TwitterAPI()
                status = twitter_api.update_status(next_question.question_text)
                next_question.twitterid = str(status.id)
                next_question.put()
            except TweepError as e:
                pass  #TODO: do something - message to monitoring?

        if current_question is not None:
            # Update overall state scores
            State.update_state_scores_for_completed_question(current_question)
            
            # Update overall question scores
            Question.tally_college_and_vote_scores(current_question)

            # Update end of question user sway scores
            users = User.get_all()
            for user in users:
                __attribute_sway_points_for_user(current_question, user)
            current_question.end_time = datetime.datetime.now()
            current_question.put()
        
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


# attribute sway points at start of new question
def __attribute_sway_points_for_user(current_question, user):
    # At least one vote on current question
    if len(user.votes) > 0 \
            and user.votes[-1].question.id() == current_question.key.id():
        user.sway_points += sway_points["submit_answer"]
        
        # Voted for winning party
        state = State.get_state_by_abbreviation(\
                    user.votes[-1].state_abbreviation)
        last_winning_party = 1 if current_question.college_score[1] > \
                             current_question.college_score[0] else 0

        # Voted on party that won last question
        if user.votes[-1].party == last_winning_party:
            user.votes[-1].winning_vote = True
            user.sway_points += sway_points["submit_winning_answer"]
             # Voted for winning party twice in a row
            if len(user.votes) == 2 and user.votes[-2].winning_vote == True:
                user.sway_points += sway_points["streak_bonus"]
            # Return used sway points
            user.sway_points += int(user.votes[-1].sway_points * \
                                    sway_points["refund"])
        else:
            user.votes[-1].winning_vote = False

        # Update user in database
        user.put()