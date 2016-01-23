from flask import Blueprint, render_template
from tweetdebate.models import Question
from tweetdebate.models import Vote

mod = Blueprint('index', __name__)

@mod.route('/')
def index():
    """Return index page."""    
    # Insert a new vote
    """question_key = Question.get_next_question().key
    state = "CA"
    userid = "jrgrafton@"
    vote = True

    # Insert Vote
    vote = Vote(question=question_key,
                state=state,
                user=userid,
                vote=vote)
    insert_key = vote.put()

    # Retrieve all votes by jrgrafton@
    votes = Vote.query_by_userid("jrgrafton@")

    # Render template
    return render_template('/index.html', insert_key=insert_key, votes=votes)"""
    return 'Hello world', 200