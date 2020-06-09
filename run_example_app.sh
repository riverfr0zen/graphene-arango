#!/bin/bash

#
# You can optionally specify the host by providing
# the IP address as an argument.
#
# E.g. ./rundev.sh 0.0.0.0

export FLASK_APP=graphene_arango/examples/example.py
export FLASK_ENV=development

if [ -z "$1" ]
    then
        flask run
    else
        flask run --host $1
fi
