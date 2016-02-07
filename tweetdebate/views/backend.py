import json
import logging
import re
import sys
import traceback

from flask import Blueprint
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import runtime

from tweetdebate.models import Question
from tweetdebate.models import State
from tweetdebate.models import User
from tweetdebate.models import Vote
from tweepy.streaming import StreamListener
from tweetdebate.tasks.twitter_stream import StdOutListener
from tweetdebate.tasks.twitter_stream import TwitterStream

mod = Blueprint('backend', __name__)
twitter_stream = None

@mod.route("/_ah/start")
def start_twitter_stream():
    # TODO: if not DEV email admin to tell of startup
    try:
        twitter_stream = TwitterStream(TwitterStreamListener())
        twitter_stream.start()
    except:
        e = sys.exc_info()[0]
        tb = traceback.format_exc()
        logging.info("except: %s %s" % (str(e), tb))    
        # TODO: email admins on exception
        start_twitter_stream()

def stop_twitter_stream():
    twitter_stream.stop()

@mod.route("/_ah/stop")
def shutdown_hook():
    # TODO: email admin to tell instance has been shutdown
    stop_twitter_stream()
    return 0
runtime.set_shutdown_hook(shutdown_hook)

class TwitterStreamListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    """
    def on_data(self, data):
        # Ensure we're always dealing with objects
        data = json.loads(str(data))
        logging.info("on_data: %s", str(data))
        self.parse_data(data)
        return True

    def on_error(self, status):
        logging.info("on_error: %s", str(status))
        # Note: 420 == rate limited (too many logins in short period)
        # TODO: email admins on_error

    def parse_data(self, data):
        # Process replies
        logging.info("parse_data: %s" % str(data))

        if "in_reply_to_status_id" in data:
            current_question = Question.get_current_question()
            reply_status_id = str(data["in_reply_to_status_id"])
            
            # Only acknowledge replies to current question
            if reply_status_id == current_question.twitterid:
                screen_name = data["user"]["screen_name"]
                state_abbreviation = self.get_state_from_string(data["text"])
                party = self.get_party_from_string_using_question(
                    data["text"], 
                    current_question)
                sway_points = self.get_sway_from_string(data["text"])
                user = User.query_by_userid(screen_name).get()

                # Cap sway points
                if user != None:
                    if user.sway_points < sway_points:
                        sway_points = user.sway_points

                # Only add vote for question if user vote was valid
                if self.add_vote_for_screenname(current_question, 
                                                str(data["id"]),
                                                state_abbreviation,
                                                party,
                                                sway_points,
                                                screen_name):
                    
                    # Add vote for question if vote was valid
                    self.add_vote_for_question(party,
                                               sway_points,
                                               state_abbreviation,
                                               current_question)

    def add_vote_for_screenname(self,
                                question,
                                replyid,
                                state_abbreviation,
                                party,
                                sway_points,
                                screen_name):
        # Require valid state and party to vote
        if state_abbreviation == None or party == None:
            return False
       
        # Require new user or user never voted on this question
        user = User.query_by_userid(screen_name).get()
        if user == None or \
                user.votes[-1].question.get().key.id() != question.key.id():

                # Add vote for user
                User.add_user_vote(user, 
                                   screen_name,
                                   Vote(
                                        question = question.key,
                                        replyid = replyid,
                                        state = state_abbreviation,
                                        party = party,
                                        sway_points = sway_points
                                    ))
                return True
        else:
            return False

    def add_vote_for_question(self,
                              party,
                              sway_points,
                              state_abbreviation,
                              question):
        # Add vote for question
        # @TODO: could optimize to O(1) by pre-populating states
        states = question.state_scores
        for state in states:
            if state.state_abbreviation == state_abbreviation:
                state.party_score_votes[party] += 1
                state.party_score_sway[party] += sway_points
                question.put()
                return

        # State had no votes previously
        states.append(State(
            state_abbreviation = state_abbreviation,
            party_score_votes = [0, 0],
            party_score_sway = [0, 0] 
        ))

        states[-1].party_score_votes[party] += 1
        states[-1].party_score_sway[party] += sway_points
        question.put()

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
        if len(result) == 1:
            hashtag = "#" + result[0]
            if ((hashtag + " " in string) or string.endswith(hashtag)):
                # Can only have one state and must be prefixed by "#"
                return result[0]
        return None

    def get_party_from_string_using_question(self, string, question):
        logging.info("get_party_from_string_using_question: %s" % string)
        string = string.lower()
        if ("#yes " in string or string.endswith("#yes")) and \
           ("#no " not in string and not string.endswith("#no")):
            return question.party
        elif ("#no " in string or string.endswith("#no")) and \
           ("#yes " not in string and not string.endswith("#yes")):
            return  1 - question.party

        # Not vote or vote was both #yes and #no
        return None

    def get_sway_from_string(self, string):
        logging.info("get_sway_from_string: %s" % string)
        string = string.upper()
        m = re.search('.*#SWAY([0-9]+).*', string)
        if m != None:
            # More than one SWAY - ignore both
            if string.count("#SWAY") == 1:
                return int(m.group(1))

        # Not vote or vote was both #yes and #no
        return 0