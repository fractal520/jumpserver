# !/usr/bin
# 
# This script install supervisor
#
# must run as sudo or root
#
# author: Niko Zhang <zhangweijie@wtsd.cn>
#
# date: 2019/02/22
#

SV_PATH=/usr/bin/supervisord

if [ -f ${SV_PATH} ];then
	echo "supervisor already install."
	exit 1;
fi

echo "yum install nss and curl first."
yum update -y nss curl

cd /tmp/
echo "Starting download&install setuptools"
wget --no-check-certificate https://bootstrap.pypa.io/ez_setup.py -O - | sudo python

if [ -f ! setuptools* ];then
	echo "setuptools not found please download it manual"
	exit 1;
fi
echo "Setuptools install finished, begain install supervisor"

easy_install supervisor

if [ ! -f ${SV_PATH} ];then
	echo "supervisor install failed."
	exit 1;
fi

SV_DIR=/etc/supervisor/config.d

mkdir -p ${SV_DIR}

if [ ! -d ${SV_DIR} ];then
	echo "${SV_DIR} not found"
	exit 1;
fi

CONF_PATH=/etc/supervisor/supervisord.conf

echo_supervisord_conf > ${CONF_PATH}

if [ -f ${CONF_PATH} ];then
	echo "${CONF_PATH} genrate success."
else
	echo "please genrate config file manual."
	exit 1;
fi

if [ ! -f supervisor ];then
	wget https://github.com/nikozhangwj/install-supervisor-script/releases/download/1.0/supervisor
fi
	
cp ./supervisor /etc/rc.d/init.d/supervisor
chmod 755 /etc/rc.d/init.d/supervisor
chkconfig supervisor on
service supervisor start
service supervisor status
echo "Install finished, please use 'service supervisor status' check it out ."
