# Generated by Django 2.1 on 2019-05-31 02:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dbops', '0010_auto_20190531_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='sqlorder',
            name='submit_user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='提交人'),
            preserve_default=False,
        ),
    ]