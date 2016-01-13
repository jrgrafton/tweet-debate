import tweepy
from tweetdebate.tasks.twitter_base import TwitterBase

class TwitterAPI(TwitterBase):
    """ A TwitterAPI wrapper class for Tweepy API.
    """
    api = None

    def __init__(self):
        TwitterBase.__init__(self)
        self.api = tweepy.API(self.auth)

    def update_status(self, status):
        return self.api.update_status(status)
        