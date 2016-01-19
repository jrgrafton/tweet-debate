 # Add libraries to path
import os
import sys
sys.path.insert(1, os.path.join(os.path.abspath('.'), 'lib')) 

import unittest2
import warnings
# silences Python's complaints about imports
warnings.filterwarnings('ignore', category=UserWarning)

USAGE = """
Path to your sdk must be the first argument. To run type:
$ apptest.py path/to/your/appengine/installation
Remember to set environment variable FLASK_CONF to TEST. 
Loading configuration depending on the value of 
environment variable allows you to add your own 
testing configuration in src/application/settings.py
"""


def main(sdk_path, test_path):
    sys.path.insert(0, sdk_path)
    import dev_appserver 
    dev_appserver.fix_sys_path()
    suite = unittest2.loader.TestLoader().discover(test_path)
    unittest2.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    # See: http://goo.gl/V5074m
    try:    
        # Path to the SDK installation
        # Defaults to /usr/local/google_appengine on OSX
        SDK_PATH = sys.argv[1]  # ...or hardcoded path
        # Path to tests folder
        TEST_PATH = os.path.join(
                    os.path.dirname(
                    os.path.abspath(__name__)),'tests')
        main(SDK_PATH, TEST_PATH)
    except IndexError:
        # you probably forgot about path as first argument
        print USAGE