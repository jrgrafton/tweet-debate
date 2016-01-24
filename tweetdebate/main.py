"""`main` is the top level module for your Flask application."""
from tweetdebate import app
from flask import render_template
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
# Insert default config to Database
