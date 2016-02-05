## Tweet Debate

AKA Pidgeon Politics

## Run Locally
**Note:** This has developed on OSX 10.11.3 - operation on other OS's not gauranteed.

1. Install the [App Engine Python SDK](https://developers.google.com/appengine/downloads).
See the README file for directions. You'll need python 2.7 and [pip 1.4 or later](http://www.pip-installer.org/en/latest/installing.html) installed too.

2. Clone this repo with

   ```
   git clone https://github.com/jrgrafton/tweet-debate
   ```
3. Install dependencies in the project's lib directory.
   Note: App Engine can only import libraries from inside your project directory.

   ```
   cd appengine-python-flask-skeleton
   pip install -r requirements.txt -t lib
   ```
4. Enable Sockets and SSL

 * Create backups of ```/path-to-gae-sdk/google/appengine/tools/devappserver2/python/sandbox.py``` and ```/path-to-gae-sdk/google/appengine/dis27/socket.py```
 * Add "_ssl" and "_socket" keys to the dictionary _WHITE_LIST_C_MODULES in ```/path-to-gae-sdk/google/appengine/tools/devappserver2/python/sandbox.py```
 * Replace ```/path-to-gae-sdk/google/appengine/dis27/socket.py``` with the socket.py file from your Python framework.

5. Run this project locally from the command line:

   ```
   dev_appserver.py app.yaml twitter_backend.yaml
   ```

Visit the application [http://localhost:8080](http://localhost:8080)

See [the development server documentation](https://developers.google.com/appengine/docs/python/tools/devserver)
for options when running dev_appserver.

## Deploy
To deploy the application:

1. Use the [Admin Console](https://appengine.google.com) to create a
   project/app id. (App id and project id are identical)
1. [Deploy the
   application](https://developers.google.com/appengine/docs/python/tools/uploadinganapp) with

   ```
   appcfg.py -A <your-project-id> app.yaml twitter_backend.yaml --oauth2 update .
   ```
1. Congratulations!  Your application is now live at your-app-id.appspot.com
