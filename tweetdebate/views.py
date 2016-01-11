from flask import render_template
from google.appengine.ext import ndb
from tweetdebate import app
from tweetdebate.models import Vote

@app.route('/')
def index():
    """Return a friendly HTTP greeting."""
    # Insert a new vote
    questionid = 123
    userid = "jrgrafton@"
    vote = True

    # Insert Vote
    vote = Vote(questionid=questionid,
                userid=userid,
                vote=vote)
    insert_key = vote.put()

    # Retrieve all votes
    votes = Vote.fetchAll().fetch(20)

    # Render template
    return render_template('/index.html', insert_key=insert_key, votes=votes)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500