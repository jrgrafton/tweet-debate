from flask import Flask
import logging
import json
import os
from tweetdebate.views import index
from tweetdebate.views import tasks
from tweetdebate.views import errors
from tweetdebate.bootstrap import Bootstrap

app = Flask(__name__)
app.register_blueprint(index.mod)
app.register_blueprint(tasks.mod)
app.register_blueprint(errors.mod)

# Insert default config to Database
@app.before_first_request
def before_first_request():
    bootstrap = Bootstrap(app)
    bootstrap.activate()