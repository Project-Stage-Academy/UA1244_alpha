# Generated by Django 5.1.2 on 2024-10-15 17:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investment_tracking', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='investmenttracking',
            old_name='investor_id',
            new_name='investor',
        ),
        migrations.RenameField(
            model_name='investmenttracking',
            old_name='startup_id',
            new_name='startup',
        ),
    ]
