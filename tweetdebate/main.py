"""`main` is the top level module for your Flask application."""
"""
import os
import logging

def is_development_server():
    return os.environ['APPLICATION_ID'].startswith('dev~')

# See http://stackoverflow.com/questions/16192916/importerror-no-module-named-ssl-with-dev-appserver-py-from-google-app-engine/24066819. The order of all of
# these things matters!
if is_development_server():
    logging.info("is_development_server: setting up local SSL")
    import sys
    import imp
    import inspect

    from google.appengine.tools.devappserver2.python import sandbox
    sandbox._WHITE_LIST_C_MODULES += ['_ssl', '_socket']

    real_os_src_path = os.path.realpath(inspect.getsourcefile(os))
    psocket = os.path.join(os.path.dirname(real_os_src_path), 'socket.py')
    logging.info("is_development_server: %s", psocket)
    imp.load_source('socket', psocket)
    phttplib = os.path.join(os.path.dirname(real_os_src_path), 'httplib.py')
    imp.load_source('httplib', phttplib)
"""
from tweetdebate import app

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
