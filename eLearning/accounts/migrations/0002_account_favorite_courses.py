# Generated by Django 3.0 on 2019-12-20 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_auto_20191220_1635'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='favorite_courses',
            field=models.ManyToManyField(to='courses.Course'),
        ),
    ]
