import datetime
import logging
from google.appengine.ext import ndb

class Question(ndb.Model):
    """Models questions"""
    image = ndb.StringProperty(indexed=False)
    question_text = ndb.StringProperty(indexed=False)
    republican = ndb.BooleanProperty(indexed=False)
    democrat = ndb.BooleanProperty(indexed=False)
    start_time = ndb.DateTimeProperty(auto_now_add=False,
                                      indexed=False)
    end_time = ndb.DateTimeProperty(auto_now_add=False,
                                      indexed=False)

    @classmethod
    def get_next_question(cls):
        return cls.query(cls.asked==False).get()

class User(ndb.Model):
    """Models an individual User"""
    userid = ndb.StringProperty()
    sway_points = ndb.IntegerProperty(default=50) # Default 50 swing points

    @classmethod
    def query_by_question(cls, question_entity):
        return cls.query(cls.question==question_entity.key)

class Vote(ndb.Model):
    """Models an individual Vote"""
    question = ndb.KeyProperty(kind=Question)
    user = ndb.KeyProperty(kind=User)
    state = ndb.StringProperty(indexed=False)
    vote = ndb.BooleanProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True, indexed=False)

    @classmethod
    def query_by_question(cls, question_entity):
        return cls.query(cls.question==question_entity.key)

    @classmethod
    def query_by_userid(cls, userid):
        return cls.query(cls.user.get().userid==userid)

class State(ndb.Model):
    """Models an individual state's score"""
    state_abbreviation = ndb.StringProperty()
    state_name = ndb.StringProperty(indexed=False)
    score_democrat = ndb.IntegerProperty(default=0, indexed=False)
    score_republican = ndb.IntegerProperty(default=0, indexed=False)

    @classmethod
    def get_state_score(cls, state_abbreviation):
        return cls.query(cls.state_abbreviation==state_abbreviation).get()

class GameStatus(ndb.Model):
    """Models current game status"""
    current_question = ndb.KeyProperty(default=None, 
                                       kind=Question,
                                       indexed=False)
    question_cadence_minutes = ndb.IntegerProperty(indexed=False)
    posted_question_count = ndb.IntegerProperty(default=0, indexed=False)
    last_question_start_time = ndb.DateTimeProperty(auto_now_add=False,
                                                    indexed=False,
                                                    default=datetime.datetime.now())
    @classmethod
    def get_game_status(cls):
        return cls.query().get()