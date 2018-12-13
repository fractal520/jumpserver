import os


class DeployBot(object):

    def __init__(self):
        self.DEPLOY_DIR = '/deploy/'
        self.DATA_DIR = '/data/'

    def commit_deploy_dir(self, app_name):
        return os.path.join(self.DEPLOY_DIR, app_name)

    def commit_app_dir(self, app_name):
        return os.path.join(self.DATA_DIR, app_name)
