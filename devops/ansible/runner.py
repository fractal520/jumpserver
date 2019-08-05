import os
from collections import namedtuple

from ansible import context
from ansible.module_utils.common.collections import ImmutableDict
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.playbook.play import Play
import ansible.constants as C

from ops.ansible.runner import AdHocRunner
from ops.ansible.exceptions import AnsibleError
from ops.ansible.callback import PlaybookResultCallBack


Options = namedtuple('Options', [
    'listtags', 'listtasks', 'listhosts', 'syntax', 'connection',
    'module_path', 'forks', 'remote_user', 'private_key_file', 'timeout',
    'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',
    'scp_extra_args', 'become', 'become_method', 'become_user',
    'verbosity', 'check', 'extra_vars', 'playbook_path', 'passwords',
    'diff', 'gathering', 'remote_tmp', 'start_at_task'
])


def get_default_options():
    options = dict(
        listtags=False,
        listtasks=False,
        listhosts=False,
        syntax=False,
        timeout=30,
        connection='ssh',
        module_path='',
        forks=10,
        remote_user='root',
        private_key_file=None,
        ssh_common_args='',
        ssh_extra_args='',
        sftp_extra_args='',
        scp_extra_args='',
        become=None,
        become_method=None,
        become_user=None,
        verbosity=1,
        extra_vars=[],
        check=False,
        playbook_path='/etc/ansible/',
        passwords=None,
        diff=False,
        gathering='implicit',
        remote_tmp='/tmp/.ansible',
        start_at_task=''
    )
    return options


# Jumpserver not use playbook
class PlayBookRunner:
    """
    用于执行AnsiblePlaybook的接口.简化Playbook对象的使用.
    """

    # Default results callback
    results_callback_class = PlaybookResultCallBack
    loader_class = DataLoader
    variable_manager_class = VariableManager
    options = get_default_options()

    def __init__(self, inventory=None, options=None):
        """
        :param options: Ansible options like ansible.cfg
        :param inventory: Ansible inventory
        """
        if options:
            self.options = options
        C.RETRY_FILES_ENABLED = False
        self.inventory = inventory
        self.loader = self.loader_class()
        self.results_callback = self.results_callback_class()
        # self.playbook_path = options.playbook_path
        self.playbook_path = options.get('playbook_path')
        self.variable_manager = self.variable_manager_class(
            loader=self.loader, inventory=self.inventory
        )
        # self.passwords = options.passwords
        self.passwords = options.get('passwords')
        self.__check()

    def __check(self):
        if self.playbook_path is None or \
                not os.path.exists(self.playbook_path):
            raise AnsibleError(
                "Not Found the playbook file: {}.".format(self.playbook_path)
            )
        if not self.inventory.list_hosts('all'):
            raise AnsibleError('Inventory is empty')

    def run(self):
        executor = PlaybookExecutor(
            playbooks=[self.playbook_path],
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            passwords={"conn_pass": self.passwords}
        )
        context.CLIARGS = ImmutableDict(self.options)

        if executor._tqm:
            executor._tqm._stdout_callback = self.results_callback
        executor.run()
        executor._tqm.cleanup()
        return self.results_callback.output


class CustomAdHocRunner(AdHocRunner):
    command_modules_choices = ('shell', 'raw', 'command', 'script', 'win_shell', 'copy', 'file')
