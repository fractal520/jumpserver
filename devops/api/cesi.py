from urllib import request
import http.cookiejar
import json

from django.conf import settings

from common.utils import get_logger

logger = get_logger('jumpserver')
cesi_url = settings.CESI_URL


class CesiAPI(object):

    def __init__(self):
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko', "Content-Type": "application/json"}
        self.cj = http.cookiejar.CookieJar()
        self.request = request
        self.opener = self.request.build_opener(request.HTTPCookieProcessor(self.cj), self.request.HTTPHandler)
        self.request.install_opener(self.opener)
        self.login()

    def login(self):
        cesi_login_url = "http://{}/api/v2/auth/login/".format(cesi_url)
        logger.debug(cesi_login_url)
        post_data = {
            "username": settings.CESI_USER,
            "password": settings.CESI_PASS
        }
        textmod = json.dumps(post_data).encode("utf-8")
        req = self.request.Request(url=cesi_login_url, data=textmod, headers=self.header)
        res = self.request.urlopen(req)
        res = res.read()
        result = res.decode(encoding='utf-8')
        logger.info(result)
        return result

    def get_tpl(self, url):
        req = self.request.Request(url=url, headers=self.header)
        retry = 0
        return_error = None
        while retry <= 3:
            try:
                res = self.request.urlopen(req)
                res = res.read()
                result = res.decode(encoding='utf-8')
                logger.info(result)
                return result
            except BaseException as error:
                logger.error(error)
                return_error = error
                retry += 1
        return False, return_error

    def get_nodes(self):
        cesi_nodes_url = "http://{}/api/v2/nodes/".format(cesi_url)
        return self.get_tpl(cesi_nodes_url)

    def get_node(self, node_name):
        cesi_node_url = "http://{}/api/v2/nodes/{}/".format(cesi_url, node_name)
        return self.get_tpl(cesi_node_url)

    def get_node_processes(self, node_name):
        cesi_node_url = "http://{}/api/v2/nodes/{}/processes/".format(cesi_url, node_name)
        return self.get_tpl(cesi_node_url)

    def get_process(self, node_name, process_name):
        cesi_node_url = "http://{}/api/v2/nodes/{}/processes/{}/".format(cesi_url, node_name, process_name)
        return self.get_tpl(cesi_node_url)

    def start_process(self, node_name, process_name):
        cesi_node_url = "http://{}/api/v2/nodes/{}/processes/{}/start/".format(cesi_url, node_name, process_name)
        return self.get_tpl(cesi_node_url)

    def stop_process(self, node_name, process_name):
        cesi_node_url = "http://{}/api/v2/nodes/{}/processes/{}/stop/".format(cesi_url, node_name, process_name)
        return self.get_tpl(cesi_node_url)

    def restart_process(self, node_name, process_name):
        cesi_node_url = "http://{}/api/v2/nodes/{}/processes/{}/restart/".format(cesi_url, node_name, process_name)
        return self.get_tpl(cesi_node_url)

    def read_process_log(self, node_name, process_name):
        cesi_node_url = "http://{}/api/v2/nodes/{}/processes/{}/log/".format(cesi_url, node_name, process_name)
        return self.get_tpl(cesi_node_url)
