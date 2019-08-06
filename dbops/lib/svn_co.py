# -*- coding: utf-8 -*-

import subprocess
from common.utils import get_logger

logger = get_logger('jumpserver')

def svn_co(svn_path, file_path, svn_username='jinky', svn_password='WTsd@12#'):
    cmd = 'svn checkout --username {svn_username} --password {svn_password} '.format(
        svn_username=svn_username,
        svn_password=svn_password
    ) + ' ' + svn_path + ' ' + file_path
    logger.info('begin checkout svn resource from ' + svn_path)
    p = subprocess.getstatusoutput(cmd)
    logger.info('checkout svn resource. ' + 'code:' + str(p[0]) + ' message: ' + p[1])
    logger.info('finish checkout svn resource to ' + file_path)
    return p


if __name__ == '__main__':
    svn_path = 'http://192.168.0.174/svn/Product/SCSS/投产资源/190710-1250'
    file_path = '/tmp/2019071602'
    svn_username = 'jinky'
    svn_password = 'WTsd@12#'
    s = svn_co(svn_path, file_path)
    print(s[0])
