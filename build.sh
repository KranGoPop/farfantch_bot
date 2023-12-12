#!/bin/bash

if [[ -n $1  &&  $1 == '-r' ]]; then
  docker-compose build;
fi;

docker-compose up