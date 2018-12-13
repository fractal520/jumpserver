#!/usr/bin/env bash

PATH1=/data/$1
PATH2=/deploy/$1
chown -R admin:admin ${PATH1}
chmod -R g+w ${PATH1}
chown -R admin:admin ${PATH2}
chmod -R g+w ${PATH2}