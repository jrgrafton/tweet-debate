from datetime import timedelta
import json
import pytz

from flask import Blueprint, render_template
from tweetdebate.models import JSONEncoder
from tweetdebate.models import Question
from tweetdebate.models import State
from tweetdebate.models import Vote

mod = Blueprint('index', __name__)

@mod.route('/')
@mod.route('/home')
def home():
    return render_template('home.html')

# @TODO move this to REST API https://cloud.google.com/appengine/docs/python/endpoints/create_api
@mod.route('/index')
def index():
    current_question = Question.get_current_question()
    local_tz = pytz.timezone('America/Los_Angeles')

    # Convert from UTC to PST
    current_question.end_time = \
        current_question.start_time.replace(
            tzinfo=pytz.utc).astimezone(local_tz)

    # Add six hours
    current_question.end_time = current_question.end_time + timedelta(hours=6)

    return render_template('index.html',
        current_question = JSONEncoder().encode(current_question.to_dict())
        #states = json.dumps(State.get_all())
    )