# Generated by Django 3.0 on 2020-01-09 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0009_auto_20191227_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseenrollment',
            name='started_at',
            field=models.DateField(auto_now_add=True),
        ),
    ]
