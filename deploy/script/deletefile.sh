#!/usr/bin/env bash

PATH=$1

if [ -f ${PATH} ];then
    /bin/rm -f ${PATH}
fi