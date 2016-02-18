"""Question API
"""
from flask import request
from datetime import datetime

from tweetdebate.models import JSONEncoder
from tweetdebate.models import Question
from tweetdebate.api import mod

"""
API functions:
  * Question: current_question (> date_modified)
  * Question: archived_questions ( end_time != None)
"""

@mod.route("/api/questions")
def get_question():
    last_modified = request.args.get('last_modified', datetime(1970,1,1))
    return JSONEncoder().encode(Question.get_current_question().to_dict()), 200 