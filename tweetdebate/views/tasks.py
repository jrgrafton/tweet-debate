from flask import Blueprint
from tweetdebate.tasks.twitter_stream import TwitterStream

mod = Blueprint('tasks', __name__)
  
@mod.route("/tasks/twitter_stream")
def twitter_stream():
    """Check if Twitter Stream task is running. If not
    restart it.
    """
    twitter_stream = TwitterStream()
    if not twitter_stream.is_running():
      twitter_stream.start()

    return 'Actvated Twitter Stream', 200