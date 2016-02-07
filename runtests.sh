#!/bin/bash
export FLASK_CONF=TEST
export TWITTER_TESTS=FALSE # Anything but FALSE enables them
python apptest.py /usr/local/google_appengine