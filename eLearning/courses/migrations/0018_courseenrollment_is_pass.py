# Generated by Django 3.0 on 2020-02-13 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0017_auto_20200203_1847'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseenrollment',
            name='is_pass',
            field=models.BooleanField(default=False),
        ),
    ]
