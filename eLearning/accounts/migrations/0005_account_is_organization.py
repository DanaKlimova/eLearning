# Generated by Django 3.0 on 2020-05-27 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='is_organization',
            field=models.BooleanField(default=False),
        ),
    ]
