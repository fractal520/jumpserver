# Generated by Django 2.1.7 on 2019-07-30 03:02

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=512)),
                ('city_code', models.IntegerField(blank=True, null=True)),
                ('city_type', models.CharField(choices=[('CORPORATION', 'CORPORATION'), ('SERVER', 'SERVER'), ('OTHER', 'OTHER')], default='CORPORATION', max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='CityMonthRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('month', models.IntegerField()),
                ('pause_count', models.IntegerField(blank=True, default=0, null=True)),
                ('total_pause_time', models.IntegerField(blank=True, default=0, null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('edit_time', models.DateTimeField(auto_now=True)),
                ('year', models.IntegerField()),
                ('report_name', models.CharField(max_length=512, null=True)),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='dreport.City', verbose_name='City Name')),
            ],
        ),
        migrations.CreateModel(
            name='CityPauseRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('risk_date', models.DateField(null=True)),
                ('recovery_date', models.DateField(blank=True, null=True)),
                ('risk_date_time', models.DateTimeField()),
                ('recovery_date_time', models.DateTimeField(blank=True, null=True, verbose_name='恢复时间')),
                ('risk_date_time_edit', models.DateTimeField(blank=True, null=True, verbose_name='熔断时间')),
                ('log_name', models.CharField(default='', max_length=256)),
                ('remark', models.CharField(blank=True, default='', max_length=256, verbose_name='备注')),
                ('risk_time', models.TimeField(null=True)),
                ('risk_level', models.CharField(blank=True, choices=[('Alert', '影响交易'), ('Warning', '影响运营及可能影响交易'), ('Info', '其他')], default=None, max_length=128, null=True, verbose_name='熔断记录等级')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='dreport.City', verbose_name='City Name')),
            ],
        ),
        migrations.CreateModel(
            name='CityWeekRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('pause_count', models.IntegerField(blank=True, default=0, null=True)),
                ('total_pause_time', models.IntegerField(blank=True, default=0, null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('edit_time', models.DateTimeField(auto_now=True)),
                ('report_name', models.CharField(max_length=512, null=True)),
                ('week_of_report', models.IntegerField()),
                ('select_date', models.DateField()),
                ('select_year', models.IntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='dreport.City', verbose_name='City Name')),
            ],
        ),
    ]