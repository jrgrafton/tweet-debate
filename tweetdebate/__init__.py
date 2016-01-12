from flask import Flask
from tweetdebate.views import index
from tweetdebate.views import tasks
from tweetdebate.views import errors

app = Flask(__name__)
app.register_blueprint(index.mod)
app.register_blueprint(tasks.mod)
app.register_blueprint(errors.mod)