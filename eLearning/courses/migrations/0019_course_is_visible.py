# Generated by Django 3.0 on 2020-05-04 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0018_courseenrollment_is_pass'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='is_visible',
            field=models.BooleanField(default=False),
        ),
    ]