import datetime
import logging
from enum import Enum
from google.appengine.ext import ndb

# Integer representations for parties
class Party(Enum):
    republication = 0
    democrate = 1

class State(ndb.Model):
    """Models an individual state's score"""
    state_abbreviation = ndb.StringProperty(indexed=False)
    party_score_votes = ndb.IntegerProperty(indexed=False, repeated=True)
    party_score_sway = ndb.IntegerProperty(indexed=False, repeated=True)

    @classmethod
    def get_state_score(cls, state_abbreviation):
        return cls.query(cls.state_abbreviation==state_abbreviation).get()

class Question(ndb.Model):
    """Models questions"""
    image = ndb.StringProperty(indexed=False)
    question_text = ndb.StringProperty(indexed=False)
    party = ndb.IntegerProperty(indexed=False)
    start_time = ndb.DateTimeProperty(auto_now_add=False,
                                      indexed=False)
    end_time = ndb.DateTimeProperty(auto_now_add=False,
                                      indexed=False)
    state_scores = ndb.LocalStructuredProperty(State, repeated=True)

    @classmethod
    def get_next_question(cls):
        return cls.query(cls.start_time==None).get()

class Vote(ndb.Model):
    """Models an individual Vote - always associated with user"""
    question = ndb.KeyProperty(kind=Question)
    state = ndb.StringProperty(indexed=False)
    party = ndb.IntegerProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True, indexed=False)

    @classmethod
    def query_by_question(cls, question_entity):
        return cls.query(cls.question==question_entity.key)

    @classmethod
    def query_by_userid(cls, userid):
        return cls.query(cls.user.get().userid==userid)

class User(ndb.Model):
    """Models an individual User"""
    userid = ndb.StringProperty()
    sway_points = ndb.IntegerProperty(default=50) # Default 50 swing points
    votes = ndb.StructuredProperty(Vote, repeated=True)
