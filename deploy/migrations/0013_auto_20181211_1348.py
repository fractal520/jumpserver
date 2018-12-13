# Generated by Django 2.1 on 2018-12-11 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0002_auto_20181030_1454'),
        ('deploy', '0012_auto_20181127_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='deploylist',
            name='bound_asset',
            field=models.ManyToManyField(blank=True, to='assets.Asset', verbose_name='Assets'),
        ),
        migrations.AddField(
            model_name='deployversion',
            name='backup_file_path',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='deployversion',
            name='version',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='deploylist',
            name='job_status',
            field=models.BooleanField(choices=[(True, True), (False, False)], default=True),
        ),
    ]
