# Generated by Django 2.1 on 2019-06-05 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbops', '0012_auto_20190603_1434'),
    ]

    operations = [
        migrations.CreateModel(
            name='SqlRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workid', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=100)),
                ('sql', models.TextField()),
                ('sequence', models.CharField(max_length=50)),
                ('error', models.TextField(null=True)),
                ('affectrow', models.CharField(max_length=100, null=True)),
                ('execute_time', models.CharField(max_length=150, null=True)),
                ('backup_dbname', models.CharField(max_length=100, null=True)),
                ('sqlsha1', models.TextField(null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='sqlorder',
            name='status',
            field=models.SmallIntegerField(choices=[(0, '未执行'), (1, '驳回'), (2, '执行中'), (3, '执行成功'), (4, '执行失败')], default=0, verbose_name='任务状态'),
        ),
        migrations.AlterField(
            model_name='sqlorder',
            name='text',
            field=models.CharField(max_length=100, verbose_name='任务说明'),
        ),
    ]
