# Generated by Django 5.1.2 on 2024-10-28 21:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='active_role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='active_users', to='users.role'),
        ),
    ]
