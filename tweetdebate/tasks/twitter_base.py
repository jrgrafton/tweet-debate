from tweepy import OAuthHandler

class TwitterBase(object):

    # Go to http://apps.twitter.com and create an app.
    # The consumer key and secret will be generated for you after
    consumer_key="FGqGxjbjnf8fCWs0ak7j3jlbs"
    consumer_secret="Gi2hHxSSnlTKDBosxkmvcwN08Ac4vRrw1giRxBruixJo5bApWx"

    # After the step above, you will be redirected to your app's page.
    # Create an access token under the the "Your access token" section
    access_token="4746890490-3eb19fbYiyigdE7cSuFL1vBxOG9Nf5RBFqcCyWM"
    access_token_secret="z81oANy3Uyywvvi36rOK3UYJoqvxKI1TACc44MOBx4pSI"

    def __init__(self):
        self.auth = OAuthHandler(self.consumer_key,
                                 self.consumer_secret)
        self.auth.set_access_token(self.access_token,
                                   self.access_token_secret)