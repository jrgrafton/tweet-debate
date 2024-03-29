from __future__ import absolute_import, print_function
from tweepy.streaming import StreamListener
from tweepy import Stream

import logging
from tweetdebate.tasks.twitter_base import TwitterBase

class TwitterStream(TwitterBase):
    """ A TwitterStream class that will continuously capture data from a
    Twitter timeline and store in our backend model.
    """
    stream = None
    listener = None

    def __init__(self, listener):
        TwitterBase.__init__(self)
        self.listener = listener

    def start(self):
        logging.info('start:')

        self.stream = Stream(self.auth, self.listener)
        self.stream.userstream(_with='user',
                          stall_warnings=True,
                          async=False)
    
    def stop(self):
        logging.info('stop:')
        self.stream.disconnect()


class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to logger.
    """
    def on_data(self, data):
        logging.info("on_data: %s", str(data))
        return True

    def on_error(self, status):
        logging.info("on_error: %s", str(status))