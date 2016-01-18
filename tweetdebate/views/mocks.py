import random

from flask import Blueprint
from tweetdebate.models import Vote
from tweetdebate.models import GameStatus

mod = Blueprint('mocks', __name__)

@mod.route("/mocks/populate_votes")
def populate_votes():
    game_status = GameStatus.get_game_status()
    # Add some votes to the datastore
    if game_status.current_question_id:
        question_id = game_status.current_question_id

        # Cast 10 random votes
        for x in range(10):
            userid = "jrg+%s@" % randrange(0, 9999999)
            vote = (randrange(1, 3) % 2) == 0
            Vote(question_id=question_id,
                        userid=userid,
                        vote=vote).put()

        return '10 votes added for current question', 200

    return 'No current question id', 200