from flask import Blueprint
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import runtime

from tweetdebate.tasks.twitter_stream import TwitterStream
from tweetdebate.tasks.twitter_stream import StdOutListener

mod = Blueprint('backend', __name__)
  
@mod.route("/_ah/start")
def twitter_backend():
    # TODO: if not DEV email admin to tell of startup
    try:
        twitter_stream = TwitterStream(StdOutListener())
        twitter_stream.start()
    except:
        e = sys.exc_info()[0]
        # TODO: email admins on exception
        twitter_backend() # Restart service
    return "test", 200

@mod.route("/_ah/stop")
def shutdown_hook():
    # TODO: email admin to tell instance has been shutdown
    return 0

runtime.set_shutdown_hook(shutdown_hook)