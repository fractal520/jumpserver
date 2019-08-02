# Generated by Django 2.1.7 on 2019-07-30 03:02

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('deploy', '0001_initial'),
        ('ops', '0006_auto_20190318_1023'),
        ('assets', '0036_auto_20190716_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnsibleRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('add_time', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(blank=True, default='', max_length=128, null=True)),
                ('desc', models.TextField(blank=True, default='', null=True, verbose_name='使用说明')),
            ],
        ),
        migrations.CreateModel(
            name='MainTask',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='任务名称')),
                ('desc', models.TextField(blank=True, null=True, verbose_name='任务简要')),
                ('adhoc_task', models.ManyToManyField(blank=True, to='ops.AdHoc', verbose_name='Ansible AdHoc任务')),
            ],
            options={
                'verbose_name': '任务列表',
                'verbose_name_plural': '任务列表',
            },
        ),
        migrations.CreateModel(
            name='PlayBookTask',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Name')),
                ('created_by', models.CharField(blank=True, default='', max_length=128, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('desc', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('run_as_admin', models.BooleanField(default=False, verbose_name='Run as admin')),
                ('run_as', models.CharField(default='', max_length=128, verbose_name='Run as')),
                ('playbook_path', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Playbook Path')),
                ('is_running', models.BooleanField(default=False, verbose_name='Is running')),
                ('extra_vars', models.CharField(blank=True, max_length=512, null=True, verbose_name='Extra Vars')),
                ('_hosts', models.TextField(blank=True, verbose_name='Hosts')),
                ('ansible_role', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='task', to='devops.AnsibleRole', verbose_name='Ansible Role')),
                ('assets', models.ManyToManyField(blank=True, to='assets.Asset', verbose_name='Assets')),
            ],
        ),
        migrations.CreateModel(
            name='TaskHistory',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False, verbose_name=uuid.uuid4)),
                ('exe_result', models.CharField(choices=[('success', '执行成功'), ('failed', '执行失败'), ('warning', '异常执行'), ('unrun', '未执行'), ('running', '正在执行')], default='unrun', max_length=10, verbose_name='任务状态')),
                ('result_info', models.TextField(blank=True, null=True, verbose_name='任务结果详情')),
                ('result_summary', models.TextField(blank=True, null=True, verbose_name='任务结果简要')),
                ('total_num', models.IntegerField(blank=True, null=True, verbose_name='执行总数')),
                ('success_num', models.IntegerField(blank=True, null=True, verbose_name='成功执行总数')),
                ('failed_num', models.IntegerField(blank=True, null=True, verbose_name='失败执行总数')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('_hosts', models.TextField(blank=True, null=True, verbose_name='Hosts')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='devops.PlayBookTask', verbose_name='Task')),
            ],
            options={
                'verbose_name': '任务历史',
                'verbose_name_plural': '任务历史',
            },
        ),
        migrations.AddField(
            model_name='maintask',
            name='playbook_task',
            field=models.ManyToManyField(blank=True, to='devops.PlayBookTask', verbose_name='Ansible Playbook任务'),
        ),
        migrations.AddField(
            model_name='maintask',
            name='version',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='deploy.DeployVersion', verbose_name='任务版本'),
        ),
    ]
