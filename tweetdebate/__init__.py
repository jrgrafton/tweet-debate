from flask import Flask

from tweetdebate.api import question

from tweetdebate.views import errors
from tweetdebate.views import index
from tweetdebate.views import tasks

from tweetdebate.bootstrap import Bootstrap

app = Flask(__name__)

# Register views
app.register_blueprint(index.mod)
app.register_blueprint(tasks.mod)
app.register_blueprint(errors.mod)

# Register APIs
app.register_blueprint(question.mod)

# Insert default config to Database
@app.before_first_request
def before_first_request():
    bootstrap = Bootstrap(app)
    bootstrap.activate()