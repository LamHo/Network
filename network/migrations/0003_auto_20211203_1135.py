# Generated by Django 3.2.8 on 2021-12-03 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_like_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='likes',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='Like',
        ),
    ]