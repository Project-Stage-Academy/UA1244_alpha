# Generated by Django 5.1.2 on 2024-10-17 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_rename_investor_project_investors_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalproject',
            name='status',
            field=models.IntegerField(choices=[(1, 'Seeking'), (2, 'In Progress'), (3, 'Finall Call'), (4, 'Closed')], default=1),
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.IntegerField(choices=[(1, 'Seeking'), (2, 'In Progress'), (3, 'Finall Call'), (4, 'Closed')], default=1),
        ),
    ]
