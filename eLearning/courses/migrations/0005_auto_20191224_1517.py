# Generated by Django 3.0 on 2019-12-24 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_auto_20191224_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseenrollment',
            name='finished_at',
            field=models.DateField(blank=True, null=True),
        ),
    ]
