import datetime
import logging
from enum import Enum
from google.appengine.ext import ndb

# @TODO: reference ENUM values rather than integers
class Party(Enum):
    republication = 0
    democrat = 1

class State(ndb.Model):
    """Models an individual state's score"""
    state_abbreviation = ndb.StringProperty()
    party_score_votes = ndb.IntegerProperty(indexed=False, repeated=True)
    party_score_sway = ndb.IntegerProperty(indexed=False, repeated=True)
    last_winning_party = ndb.IntegerProperty(indexed=False, default=None)

    @classmethod
    def get_state_by_abbreviation(cls, state_abbreviation):
        state_abbreviation = state_abbreviation.upper()
        return cls.query(cls.state_abbreviation == state_abbreviation).get()

    @classmethod
    def is_valid_state(cls, state_abbreviation):
        # Reduce datastore operations by harcoding valid states
        states = ["AL","AK","AS","AZ","AR","CA","CO","CT","DE","DC",
                "FM","FL","GA","GU","HI","ID","IL","IN","IA","KS",
                "KY","LA","ME","MH","MD","MA","MI","MN","MS","MO",
                "MT","NE","NV","NH","NJ","NM","NY","NC","ND","MP",
                "OH","OK","OR","PW","PA","PR","RI","SC","SD","TN",
                "TX","UT","VT","VI","VA","WA","WV","WI","WY"]

        return state_abbreviation.upper() in states

    # Updates state scores based on result of a question
    @classmethod
    def update_state_scores(cls, question_state_scores):
        # Loops over each state that was voted for in this question
        for question_state_score in question_state_scores:
            state = cls.query(cls.state_abbreviation == \
                    question_state_score.state_abbreviation).get()
            total_scores = []
            total_scores.append(question_state_score.party_score_votes[0] + \
                              question_state_score.party_score_sway[0])
            total_scores.append(question_state_score.party_score_votes[1] + \
                              question_state_score.party_score_sway[1])

            # Ties get no points
            if total_scores[0] > total_scores[1]:
                state.party_score_votes[Party.republication] += 1
                state.last_winning_party = 0
            elif total_scores[1] > total_scores[0]:
                state.party_score_votes[1] += 1
                state.last_winning_party = 1
            
            # Always tally total sway for a state
            state.party_score_sway[0] += \
                question_state_score.party_score_sway[0]
            state.party_score_sway[1] += \
                question_state_score.party_score_sway[1]

            state.put()

class Question(ndb.Model):
    """Models questions"""
    twitterid = ndb.StringProperty(indexed=False)
    image = ndb.StringProperty(indexed=False)
    question_text = ndb.StringProperty(indexed=False)
    party = ndb.IntegerProperty(indexed=False)
    start_time = ndb.DateTimeProperty(auto_now_add=False, default=None)
    end_time = ndb.DateTimeProperty(auto_now_add=False, default=None)
    state_scores = ndb.LocalStructuredProperty(State, repeated=True)

    @classmethod
    def get_current_question(cls):
        return cls.query(ndb.AND(
                           cls.start_time != None,
                           cls.end_time == None)).get()

    @classmethod
    def get_next_question(cls):
        return cls.query(cls.start_time == None).get()

    @classmethod
    def get_current_question_start_time(cls):
        entity = Question.get_current_question()
        if entity is not None:
            return entity.start_time
        else:
            return None

class Vote(ndb.Model):
    """Models an individual Vote - always associated with user"""
    question = ndb.KeyProperty(kind=Question)
    replyid = ndb.StringProperty(indexed=False)
    state_abbreviation = ndb.StringProperty(indexed=False)
    party = ndb.IntegerProperty(indexed=False)
    sway_points = ndb.IntegerProperty(indexed=False)
    winning_vote = ndb.BooleanProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True, indexed=False)

    @classmethod
    def query_by_question(cls, question_entity):
        return cls.query(cls.question==question_entity.key)

class User(ndb.Model):
    """Models an individual User"""
    userid = ndb.StringProperty() #@TODO: change this to screen_name
    sway_points = ndb.IntegerProperty(indexed=False, default=50)
    votes = ndb.StructuredProperty(Vote, indexed=False, repeated=True)
    last_retweet_id = ndb.StringProperty(indexed=False, default=None)

    @classmethod
    def get_starting_sway_points(cls):
        return 50

    @classmethod
    def get_all(cls):
        return cls.query().fetch()

    @classmethod
    def query_by_userid(cls, userid):
        return cls.query(cls.userid==userid)

    @classmethod
    def add_user_vote(cls, user, userid, vote):
        if user is None:
            user = User(
                userid = userid,
                votes = [vote],
                # Can use sway points upon creation
                sway_points = (User.get_starting_sway_points() - \
                               vote.sway_points)
            )
            user.put()
        else:
            user.votes.append(vote)
            user.sway_points -= vote.sway_points
            user.put()
