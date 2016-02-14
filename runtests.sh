#!/bin/bash
export FLASK_CONF=TEST
export TWITTER_TESTS=FALSE # Anything but FALSE enables Twitter tests

find tweetdebate/. -name '*.pyc' -delete # Remove cached files
python apptest.py /usr/local/google_appengine