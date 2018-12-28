#!/usr/bin/env bash

backup_path=$1
backup_directory=$2
app_name=$3

cd ${backup_directory}

tar -xvzf ${backup_path}
if [ -d /data/${app_name}/config ];then
    cp -rf ${backup_directory}/data/${app_name}/config/* /data/${app_name}/config/
else
    cp -rf ${backup_directory}/data/${app_name}/config /data/${app_name}/
fi

if [ -d /data/${app_name}/lib ];then
    rm -rf /data/${app_name}/lib
fi
cp -rf ${backup_directory}/data/${app_name}/lib /data/${app_name}/