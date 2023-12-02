#!/bin/bash

if [[ -n $1  &&  $1 == '-r' ]]; then
  sudo docker-compose build;
fi;

sudo docker-compose up