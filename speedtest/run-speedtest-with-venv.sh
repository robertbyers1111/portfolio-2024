#!/bin/bash

DIR=/localstore/MEGA/MEGAsync/git/source/projects/portfolio-2024/speedtest
BASE=speedtest-runner.py
EXE=$DIR/$BASE

cd $DIR
source $DIR/.venv/bin/activate
ps -efj | grep -q "python3 .*${BASE}$"
[ $? -ne 0 ] && {
    $EXE 2>&1 >> $DIR/console.log 2>&1
}
