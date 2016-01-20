from flask import Blueprint, render_template
from tweetdebate.models import Vote

mod = Blueprint('index', __name__)

@mod.route('/')
def index():
    """Return index page."""
    # Insert a new vote
    question_id = 123
    userid = "jrgrafton@"
    vote = True

    # Insert Vote
    """vote = Vote(question_id=question_id,
                user=userid,
                vote=vote)
    insert_key = vote.put()

    # Retrieve all votes by jrgrafton@
    votes = Vote.query_by_user("jrgrafton@")

    # Render template
    return render_template('/index.html', insert_key=insert_key, votes=votes)"""