import datetime
import logging
from enum import Enum
from google.appengine.ext import ndb

# Integer representations for parties
class Party(Enum):
    republication = 0
    democrat = 1

class State(ndb.Model):
    """Models an individual state's score"""
    state_abbreviation = ndb.StringProperty()
    party_score_votes = ndb.IntegerProperty(indexed=False, repeated=True)
    party_score_sway = ndb.IntegerProperty(indexed=False, repeated=True)

    @classmethod
    def get_state_by_abbreviation(cls, state_abbreviation):
        return cls.query(cls.state_abbreviation == state_abbreviation).get()

    @classmethod
    def is_valid_state(cls, state_abbreviation):
        entity = \
                cls.query(cls.state_abbreviation == state_abbreviation).get()
        return entity is not None

    # Updates state scores based on result of a question
    @classmethod
    def update_state_scores(cls, question_state_scores):
        for question_state_score in question_state_scores:
            state = cls.query(cls.state_abbreviation == \
                    question_state_score.state_abbreviation).get()
            if question_state_score.party_score_votes[0] > \
                    question_state_score.party_score_votes[1]:
                state.party_score_votes[0]+=1
            elif question_state_score.party_score_votes[1] > \
                    question_state_score.party_score_votes[0]:
                state.party_score_votes[1]+=1
            # Ties get no points
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
    state = ndb.StringProperty(indexed=False)
    party = ndb.IntegerProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True, indexed=False)

    @classmethod
    def query_by_question(cls, question_entity):
        return cls.query(cls.question==question_entity.key)

class User(ndb.Model):
    """Models an individual User"""
    userid = ndb.StringProperty()
    sway_points = ndb.IntegerProperty(indexed=False, default=50) # Default 50 swing points
    votes = ndb.StructuredProperty(Vote, indexed=False, repeated=True)

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
                votes = [vote]
            )
            user.put()
        else:
            user.votes.append(vote)
            user.put()
