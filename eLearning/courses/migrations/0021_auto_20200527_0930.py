# Generated by Django 3.0 on 2020-05-27 09:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20200527_0430'),
        ('courses', '0020_auto_20200527_0416'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='owner_organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.Organization'),
        ),
        migrations.AlterField(
            model_name='course',
            name='owner_type',
            field=models.CharField(choices=[('usr', 'user'), ('org', 'org')], max_length=3),
        ),
        migrations.AlterField(
            model_name='course',
            name='type',
            field=models.CharField(choices=[('pbl', 'public'), ('prv', 'private')], default='pbl', max_length=3),
        ),
    ]