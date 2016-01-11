from google.appengine.ext import ndb

class Vote(ndb.Model):
    """Models an individual Vote with questionid, vote, userid, date"""
    questionid = ndb.IntegerProperty()
    userid = ndb.StringProperty()
    vote = ndb.BooleanProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def fetchAll(cls):
        return cls.query().order(-cls.date)