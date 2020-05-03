# Generated by Django 3.0 on 2019-12-24 09:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0002_auto_20191220_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='owner_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='managed_courses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(related_name='individual_courses', to=settings.AUTH_USER_MODEL),
        ),
    ]
