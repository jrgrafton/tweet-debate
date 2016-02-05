import os
import tweepy
from tweetdebate.tasks.twitter_base import TwitterBase

class TwitterAPI(TwitterBase):
    """ A TwitterAPI wrapper class for Tweepy API.
    """
    api = None

    def __init__(self):
        TwitterBase.__init__(self)
        self.api = tweepy.API(self.auth)

    def update_status(self, status, in_reply_to_status_id = None):
        return self.api.update_status(status, in_reply_to_status_id)

    def get_last_tweet(self):
        return self.api.user_timeline(id = self.api.me().id, count = 1)[0]

    def delete_all_tweets(self):
        if "Development" in os.getenv('SERVER_SOFTWARE'):
            # Function disabled in production
            timeline = self.api.user_timeline(count = 10)
            for status in timeline:
                self.api.destroy_status(status.id)
        