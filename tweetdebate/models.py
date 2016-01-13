from google.appengine.ext import ndb

class Vote(ndb.Model):
    """Models an individual Vote with questionid, vote, userid, date"""
    questionid = ndb.IntegerProperty()
    userid = ndb.StringProperty()
    vote = ndb.BooleanProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True, indexed=False)

    @classmethod
    def query_by_user(cls, userid):
        return cls.query(cls.userid==userid)

class Question(ndb.Model):
    """Models current game status"""
    questionid = ndb.IntegerProperty()
    image = ndb.StringProperty(indexed=False)
    question_text = ndb.StringProperty(indexed=False)
    republican = ndb.BooleanProperty()
    democrat = ndb.BooleanProperty()

class GameStatus(ndb.Model):
    """Models current game status"""
    states = ndb.JsonProperty(indexed=False)
    question_cadence_minutes = ndb.IntegerProperty(indexed=False)
    completed_question_count = ndb.IntegerProperty(indexed=False)
    last_question_start_time = ndb.DateTimeProperty(auto_now_add=False,
                                                    indexed=False)