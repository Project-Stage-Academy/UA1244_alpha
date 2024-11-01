# Generated by Django 5.1.2 on 2024-10-31 19:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('investors', '0002_alter_investorprofile_investor_logo'),
        ('projects', '0003_alter_historicalproject_status_alter_project_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackProjects',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saved_at', models.DateTimeField(auto_now_add=True)),
                ('investor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='investors.investorprofile')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
            ],
            options={
                'verbose_name': 'Track Project',
                'verbose_name_plural': 'Track Project',
                'ordering': ['-saved_at'],
                'constraints': [models.UniqueConstraint(fields=('investor', 'project'), name='unique_investor_project')],
            },
        ),
    ]