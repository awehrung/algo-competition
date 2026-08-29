#!/bin/bash

if [ $# -eq 0 ]; then
  echo 'Missing arguments. Example usages:'
  echo 'Game 1: ./test.sh "[B,C,C]" "[C,B,C]"'
  echo 'Game 2: ./test.sh 30/2/S 30/1/P 20/0/P'
  echo 'Game 3: ./test.sh R=4 MM=23 MQ=2 OM=15 OQ=4 10/5 15/16 3/14'
  exit 1
fi

python src/main.py "$@"
