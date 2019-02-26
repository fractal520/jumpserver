from urllib import request
import http.cookiejar
import json


class CesiAPI(object):

    def __init__(self):
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko', "Content-Type": "application/json"}
        self.cj = http.cookiejar.CookieJar()
        self.request = request
        self.opener = self.request.build_opener(request.HTTPCookieProcessor(self.cj), self.request.HTTPHandler)
        self.request.install_opener(self.opener)

    def login(self):
        cesi_login_url = "http://10.128.1.198:5000/api/v2/auth/login/"
        post_data = {
            "username": "admin",
            "password": "admin"
        }
        textmod = json.dumps(post_data).encode("utf-8")
        req = self.request.Request(url=cesi_login_url, data=textmod, headers=self.header)
        res = self.request.urlopen(req)
        res = res.read()
        result = res.decode(encoding='utf-8')
        print(result)
        return result

    def get_tpl(self, url):
        req = self.request.Request(url=url, headers=self.header)
        try:
            res = self.request.urlopen(req)
        except BaseException as error:
            return False, error
        res = res.read()
        result = res.decode(encoding='utf-8')
        print(result)
        return result

    def get_nodes(self):
        cesi_nodes_url = "http://10.128.1.198:5000/api/v2/nodes/"
        return self.get_tpl(cesi_nodes_url)

    def get_node(self, node_name):
        cesi_node_url = "http://10.128.1.198:5000/api/v2/nodes/{}/".format(node_name)
        return self.get_tpl(cesi_node_url)

    def get_node_processes(self, node_name):
        cesi_node_url = "http://10.128.1.198:5000/api/v2/nodes/{}/processes/".format(node_name)
        return self.get_tpl(cesi_node_url)

    def get_process(self, node_name, process_name):
        cesi_node_url = "http://10.128.1.198:5000/api/v2/nodes/{}/processes/{}/".format(node_name, process_name)
        return self.get_tpl(cesi_node_url)

    def start_process(self, node_name, process_name):
        cesi_node_url = "http://10.128.1.198:5000/api/v2/nodes/{}/processes/{}/start/".format(node_name, process_name)
        return self.get_tpl(cesi_node_url)

    def stop_process(self, node_name, process_name):
        cesi_node_url = "http://10.128.1.198:5000/api/v2/nodes/{}/processes/{}/stop/".format(node_name, process_name)
        return self.get_tpl(cesi_node_url)

    def restart_process(self, node_name, process_name):
        cesi_node_url = "http://10.128.1.198:5000/api/v2/nodes/{}/processes/{}/restart/".format(node_name, process_name)
        return self.get_tpl(cesi_node_url)

    def read_process_log(self, node_name, process_name):
        cesi_node_url = "http://10.128.1.198:5000/api/v2/nodes/{}/processes/{}/log/".format(node_name, process_name)
        return self.get_tpl(cesi_node_url)
