#!/bin/bash

if [ $1 == '-r' ]; then
  sudo docker-compose build;
fi;

sudo docker-compose up