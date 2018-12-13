#!/usr/bin/env bash

APP_name=${1}
version=${2}
tar_file=/deploy/${APP_name}/app/${version}.tar.gz
file_path=/deploy/${APP_name}/app/${version}
target_dir=/data/${APP_name}/

tar -xvzf ${tar_file} -C /
if [ -d "${file_path}/config/" ];then
cp -rf ${file_path}/config/* ${target_dir}/config/
fi
if [ -d "${file_path}/lib/" ];then
cp -rf ${file_path}/lib/* ${target_dir}/lib/
fi