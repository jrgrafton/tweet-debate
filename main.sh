#!/bin/bash
echo "Clear datastore on startup? [y] or [n]"
read clear_datastore
clear_datastore=`echo $clear_datastore | tr '[:lower:]' '[:lower:]'`

if [ $clear_datastore = "y" ]; then
    cmd="dev_appserver.py --clear_datastore yes app.yaml twitter_backend.yaml"
else
    cmd="dev_appserver.py app.yaml twitter_backend.yaml"
fi
echo "executing \"$cmd\""
exec $cmd