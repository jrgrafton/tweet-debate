<?php
  require __DIR__ . '/vendor/autoload.php';
  error_reporting(E_ALL);
  echo 'Hello, world<br />';
  
  // Write it to Datastore
  $obj_store = new GDS\Store('Votes');
  $obj_store->upsert($obj_store->createEntity([
    'questionId' => 124,
    'vote' => true,
    'user' => 'jrgrafton@',
    'time' => new DateTime('-2 hours')
  ]));

  // Fetch vote from data store
  echo "printing vote";
  $vote = $obj_store->fetchAll("SELECT * FROM Votes");
  var_dump($vote);
?>

