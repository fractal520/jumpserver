#!/usr/bin/env bash

backup_path=$1
backup_directory=$2
app_name=$3

cd ${backup_directory}

tar -xvzf ${backup_path}
cp -rf ${backup_directory}/data/${app_name}/config/* /data/${app_name}/config/