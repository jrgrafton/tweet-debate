from __future__ import absolute_import, print_function

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import logging

class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to logger.
    """
    def on_data(self, data):
        logging.info("on_data: %s", str(data))
        return True

    def on_error(self, status):
        logging.info("on_error: %s", str(status))

class TwitterStream():
    """ A TwitterStream class that will continuously capture data from a
    Twitter timeline and store in our backend model.
    """
    # Go to http://apps.twitter.com and create an app.
    # The consumer key and secret will be generated for you after
    consumer_key="FGqGxjbjnf8fCWs0ak7j3jlbs"
    consumer_secret="Gi2hHxSSnlTKDBosxkmvcwN08Ac4vRrw1giRxBruixJo5bApWx"

    # After the step above, you will be redirected to your app's page.
    # Create an access token under the the "Your access token" section
    access_token="4746890490-3eb19fbYiyigdE7cSuFL1vBxOG9Nf5RBFqcCyWM"
    access_token_secret="z81oANy3Uyywvvi36rOK3UYJoqvxKI1TACc44MOBx4pSI"

    def start(self):
        logging.info('start:')
        l = StdOutListener()
        auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)

        stream = Stream(auth, l)
        stream.userstream(_with='user',
                          stall_warnings=True,
                          async=False)

    def is_running(self):
        return False
