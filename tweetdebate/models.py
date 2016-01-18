import logging
from google.appengine.ext import ndb

class Question(ndb.Model):
    """Models current game status"""
    image = ndb.StringProperty(indexed=False)
    question_text = ndb.StringProperty(indexed=False)
    republican = ndb.BooleanProperty(indexed=False)
    democrat = ndb.BooleanProperty(indexed=False)
    asked = ndb.BooleanProperty()

    @classmethod
    def get_next_question(cls):
        return cls.query(cls.asked==False).get()
        
class Vote(ndb.Model):
    """Models an individual Vote with question_id, vote, userid, date"""
    question_id = ndb.KeyProperty(kind=Question)
    userid = ndb.StringProperty()
    vote = ndb.BooleanProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True, indexed=False)

    @classmethod
    def query_by_user(cls, userid):
        return cls.query(cls.userid==userid)

class GameStatus(ndb.Model):
    """Models current game status"""
    states = ndb.JsonProperty(indexed=False)
    current_question_id = ndb.IntegerProperty(indexed=False)
    question_cadence_minutes = ndb.IntegerProperty(indexed=False)
    posted_question_count = ndb.IntegerProperty(indexed=False)
    last_question_start_time = ndb.DateTimeProperty(auto_now_add=False,
                                                    indexed=False)
    @classmethod
    def get_game_status(cls):
        return cls.query().get()

    """@classmethod
    def get_next_state(cls):
        game_status = cls.query().get()
        posted_question_count = game_status.posted_question_count
        states = game_status.states
        state_count = len(game_status.states)
        return states[posted_question_count % state_count]"""