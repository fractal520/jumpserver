import uuid
import json
import os
import datetime
import yaml
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from common.utils import get_logger
from ops.ansible.runner import get_default_options, PlayBookRunner
from ops.inventory import JMSInventory
from ops.ansible import AnsibleError


logger = get_logger(__file__)


playbook_dir = os.path.join(settings.PROJECT_DIR, 'data', 'playbooks')

if not os.path.isdir(playbook_dir):
    os.makedirs(playbook_dir)


class AnsibleRole(models.Model):

    name = models.CharField(max_length=200, verbose_name=_('Name'))
    add_time = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=128, blank=True, null=True, default='')
    desc = models.TextField(verbose_name="使用说明", blank=True, null=True, default='')

    def __str__(self):
        return str(self.name) + '(创建者:'+str(self.created_by)+')'


class PlayBookTask(models.Model):

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=128, unique=True, verbose_name=_('Name'))
    created_by = models.CharField(max_length=128, blank=True, null=True, default='')
    date_created = models.DateTimeField(auto_now_add=True)
    desc = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    ansible_role = models.ForeignKey(
        AnsibleRole, verbose_name=_('Ansible Role'), related_name='task',
        on_delete=models.DO_NOTHING
    )
    run_as_admin = models.BooleanField(default=False, verbose_name=_('Run as admin'))
    run_as = models.CharField(max_length=128, default='', verbose_name=_("Run as"))
    playbook_path = models.CharField(max_length=1000, verbose_name=_('Playbook Path'), blank=True, null=True)
    is_running = models.BooleanField(default=False, verbose_name=_('Is running'))
    extra_vars = models.CharField(max_length=512, verbose_name=_('Extra Vars'), blank=True, null=True)
    assets = models.ManyToManyField('assets.Asset', blank=True, verbose_name=_("Assets"))
    _hosts = models.TextField(blank=True, verbose_name=_('Hosts'))  # ['hostname1', 'hostname2']

    @property
    def hosts(self):
        return json.loads(self._hosts)

    @hosts.setter
    def hosts(self, item):
        self._hosts = json.dumps(item)

    # 获取默认options
    @property
    def options(self):
        return get_default_options()

    # 使用JMSInventory构建inventory
    @property
    def inventory(self):
        hostname_list = [asset.fullname for asset in self.assets.all()]
        return JMSInventory(
            hostname_list=hostname_list,
            run_as_admin=self.run_as_admin,
            run_as=self.run_as,
            become_info=None
        )

    @property
    def hex_id(self):
        return self.id.hex

    def create_playbook(self, ansible_role):
        self.playbook_path = os.path.join(playbook_dir, self.hex_id + '.yml')
        yml_tpl = [{'hosts': 'all', 'roles': [{'role': ansible_role.name}]}]
        with open(self.playbook_path, 'wt') as fhandler:
            yaml.dump(yml_tpl, fhandler)
        self.save()
        return True

    def record(self, result="", error=None):
        hid = str(uuid.uuid4())
        total_num = 0
        success_num = 0
        failed_num = 0
        summery_result = ""

        if result:

            for host, value in result.get('stats').items():
                total_num += value['ok'] + value['failures'] + value['unreachable']
                success_num += value['ok']
                failed_num += value['failures']

            plays = result.get('plays')

            for play in plays:
                tasks = play.get('tasks')
                for task in tasks:
                    # print(task)
                    title = 'Task: ' + task.get('task')['name']
                    summery_result += title
                    print(title)
                    hosts = task.get('hosts')
                    for hostname, r in hosts.items():
                        if r.get('stderr'):
                            error_msg = r.get('stderr')
                            line = "{}:{}\n".format(hostname, error_msg[0:100])
                        elif r.get('stdout'):
                            line = "{}:{}...\n".format(hostname, r.get('stdout')[0:50])
                        else:
                            line = "{}:{}\n".format(hostname, "sucess")
                        if not r.get('skipped_reason'):
                            summery_result += line
                            print(line)

        if result and not error:
            if failed_num == 0:
                exe_result = 'success'
            else:
                exe_result = 'failed'
            history = TaskHistory.objects.create(
                id=hid,
                task=self,
                exe_result=exe_result,
                result_info=summery_result,
                result_summary=json.dumps(result.get('stats')),
                total_num=total_num,
                success_num=success_num,
                failed_num=failed_num
            )
            logger.info("创建{}历史记录成功".format(history.id))
        elif error and result:
            history = TaskHistory.objects.create(
                id=hid,
                task=self,
                exe_result='failed',
                result_info=result,
                result_summary=json.dumps(result.get('stats')),
                total_num=total_num,
                success_num=success_num,
                failed_num=failed_num
            )
            logger.error("创建{}错误历史记录成功".format(history.id))

    def run(self):
        return self._run_only()

    def _run_only(self):
        date_start = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("{} Start task: {}\r\n".format(date_start, self.name))
        self.is_running = True
        self.save()

        options = self.options

        if not self.playbook_path:
            self.create_playbook(self.ansible_role)

        # 判断playbook是否存在
        if not os.path.exists(self.playbook_path) or not os.path.isfile(self.playbook_path):
            self.is_running = False
            self.save()
            print("Role File Not Found!\nPlease check playbook_path: {}.".format(self.playbook_path))
            raise FileNotFoundError('Please check playbook_path {}.'.format(self.playbook_path))

        # 将playbook_path传入options
        options = options._replace(playbook_path=self.playbook_path)
        runner = PlayBookRunner(self.inventory, options=options)

        # 将额外变量传入变量控制器
        if self.extra_vars:
            runner.variable_manager.extra_vars = eval(self.extra_vars)
            logger.debug(json.dumps(runner.variable_manager.get_vars()))
        try:
            result = runner.run()
            logger.debug(json.dumps(result, indent=4))
            logger.info(json.dumps(result.get('stats'), indent=4))
            self.record(result)
            self.is_running = False
            self.save()
            print(json.dumps(result.get('stats'), indent=4))
            date_end = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("\r\n{} Task finished".format(date_end))
            return result
        except AnsibleError as e:
            self.record(error=True, result=str(e))
            self.is_running = False
            self.save()
            date_end = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("\r\n{} Task finished".format(date_end))
            logger.warn("Failed run playbook {}, {}".format(self.name, e))

    def __str__(self):
        return self.name


class TaskHistory(models.Model):

    id = models.UUIDField(uuid.uuid4, primary_key=True)
    task = models.ForeignKey(PlayBookTask, verbose_name="Task", on_delete=models.CASCADE)
    exe_result = models.CharField(max_length=10, choices=(
        ('success', '执行成功'), ('failed', '执行失败'), ('warning', '异常执行'),
        ('unrun', '未执行'), ('running', '正在执行')), default='unrun', verbose_name="任务状态")
    result_info = models.TextField(null=True, blank=True, verbose_name="任务结果详情")
    result_summary = models.TextField(null=True, blank=True, verbose_name="任务结果简要")
    total_num = models.IntegerField(null=True, blank=True, verbose_name="执行总数")
    success_num = models.IntegerField(null=True, blank=True, verbose_name="成功执行总数")
    failed_num = models.IntegerField(null=True, blank=True, verbose_name="失败执行总数")
    create_time = models.DateTimeField(auto_now_add=True)
    _hosts = models.TextField(null=True, blank=True, verbose_name=_('Hosts'))  # ['hostname1': {}, 'hostname2': {}]

    @property
    def failed_host(self):
        failed_host = []
        if self.result_summary:
            summary = json.loads(self.result_summary)
            for host, value in summary.items():
                if value["failures"] != 0 or value["unreachable"] != 0:
                    failed_host.append(host)
        return failed_host

    @property
    def success_host(self):
        success_host = []
        if self.result_summary:
            summary = json.loads(self.result_summary)
            for host, value in summary.items():
                if value["failures"] == 0 and value["unreachable"] == 0:
                    success_host.append(host)
        return success_host

    @property
    def short_id(self):
        return str(self.id).split('-')[-1]

    @property
    def hosts(self):
        return json.loads(self._hosts)

    @hosts.setter
    def hosts(self, item):
        self._hosts = json.dumps(item)

    class Meta:
        verbose_name = '任务历史'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{}(执行时间{})'.format(self.task.name, self.create_time)
