# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
from flask import Flask

from tweetdebate import app
from tweetdebate.views import backend

app = Flask(__name__)
app.register_blueprint(backend.mod)