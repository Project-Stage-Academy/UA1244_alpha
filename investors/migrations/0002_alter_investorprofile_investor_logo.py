# Generated by Django 5.1.2 on 2024-10-14 01:01

from django.db import migrations, models
import common

import common

from common.validators.image_validator import ImageValidator


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investorprofile',
            name='investor_logo',
            field=models.ImageField(blank=True, null=True, upload_to='investor_logos/', validators=[ImageValidator(max_height=800, max_size=5242880, max_width=1200)]),
        ),
    ]
