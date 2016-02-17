/** google global namespace for Google projects. */
var google = google || {};

/** appengine namespace for Google Developer Relations projects. */
google.appengine = google.appengine || {};

/** samples namespace for App Engine sample code. */
google.appengine.samples = google.appengine.samples || {};

/** hello namespace for this sample. */
google.appengine.samples.hello = google.appengine.samples.hello || {};

google.appengine.samples.hello.init = function(apiRoot) {
  // Loads the OAuth and helloworld APIs asynchronously, and triggers login
  // when they have completed.
  var apisToLoad;
  var callback = function() {
    if (--apisToLoad == 0) {
        // Get first greeting when API's have loaded
        gapi.client.helloworld.greetings.getGreeting({'id': 0}).execute(
            function(resp) {
                console.log(resp)
            }
        )
    }
  }

  apisToLoad = 1; // must match number of calls to gapi.client.load()
  gapi.client.load('helloworld', 'v1', callback, apiRoot);
};

function init() {
    //gapi.client.load('quoteendpoint', 'v1', functiom() {
    //}, 'http://localhost:8888/_ah/api');
    console.log("Testing APIS")
    google.appengine.samples.hello.init('//' + window.location.host + '/_ah/api');
}