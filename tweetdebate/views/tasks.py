import datetime
import logging
import os
import re
import time

from flask import Blueprint
from flask import request
from tweetdebate.models import Question
from tweetdebate.models import State
from tweetdebate.models import User
from tweetdebate.models import Vote
from tweetdebate.tasks.twitter_api import TwitterAPI
from tweetdebate.tasks.twitter_stream import TwitterStream
from tweepy import TweepError
from tweepy.streaming import StreamListener

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
        
        if post_to_twitter != False:
            try:
                twitter_api = TwitterAPI()
                status = twitter_api.update_status(next_question.question_text)
                next_question.twitterid = str(status.id)
                next_question.put()
            except TweepError as e:
                pass  #TODO: do something - message to monitoring?

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
    """ Activate Twitter Stream Daemon
    """
    # Start or stop stream?
    action = request.args.get('action', "start")

    pid_file = os.path.dirname(os.path.realpath(__file__)) + \
            "/../../daemon-twitterstream.pid"
    twitter_stream = TwitterStream(TwitterStreamListener(), pid_file)

    if action == "start":
        #twitter_stream.start()
        twitter_stream.run()
        return 'Started Twitter Stream', 200
    else:
        twitter_stream.stop()
        return 'Stopped Twitter Stream', 200

class TwitterStreamListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    """
    def on_data(self, data):
        logging.info("on_data: %s", str(data))
        self.parse_data(data)
        return True

    def on_error(self, status):
        logging.info("on_error: %s", str(status))

    def parse_data(self, data):
        # Process replies
        if "in_reply_to_status_id" in data:
            current_question = Question.get_current_question()
            reply_status_id = str(data["in_reply_to_status_id"])

            # Only acknowledge replies to current question
            if reply_status_id == current_question.twitterid:
                screen_name = data["user"]["screen_name"]
                state = self.get_state_from_string(data["text"])
                party = self.get_party_from_string_using_question(
                    data["text"], 
                    current_question)
                
                # Ignore reply unless valid party and state is specified
                if state != None and party != None:
                    user = User.query_by_userid(screen_name).get()
                    
                    # User has never voted or never voted for this question
                    if user == None or \
                        user.votes[-1].question.get().twitterid != \
                        reply_status_id:
                        
                        User.add_user_vote(user, screen_name, Vote(
                            question = current_question.key,
                            replyid = str(data["id"]),
                            state = "WA",
                            party = 1
                        ))

    def get_state_from_string(self, string):
        states = ["AL","AK","AS","AZ","AR","CA","CO","CT","DE","DC",
                "FM","FL","GA","GU","HI","ID","IL","IN","IA","KS",
                "KY","LA","ME","MH","MD","MA","MI","MN","MS","MO",
                "MT","NE","NV","NH","NJ","NM","NY","NC","ND","MP",
                "OH","OK","OR","PW","PA","PR","RI","SC","SD","TN",
                "TX","UT","VT","VI","VA","WA","WV","WI","WY"]
        string = string.upper()
        regex = re.compile(r'\b(' + '|'.join(states) + r')\b')
        result = regex.findall(string)
        if len(result) == 1 and ("#" + result[0] + " ") in string:
            # Can only have one state and must be prefixed by "#"
            return result[0]
        
        return None

    def get_party_from_string_using_question(self, string, question):
        question_party = question.party
        string = string.lower()
        if "#yes " in string and "#no " not in string:
            return question.party
        elif "#no " in string and "#yes " not in string:
            return  1 - question_party

        # Not vote or vote was both #yes and #no
        return None
