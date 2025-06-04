#!/bin/bash

if [ $# -eq 0 ]; then
  echo 'Missing arguments. Example usages:'
  echo 'Game 1: ./test.sh "[B,C,C]" "[C,B,C]"'
  echo 'Game 2: ./test.sh 30/2/S 30/1/P 20/0/P'
	exit 1
fi

node src/main.js "$@"
