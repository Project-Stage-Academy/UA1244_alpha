# Generated by Django 5.1.2 on 2024-10-15 04:47

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0002_alter_investorprofile_investor_logo'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='investor',
            new_name='investors',
        ),
        migrations.RemoveField(
            model_name='historicalproject',
            name='media_files',
        ),
        migrations.RemoveField(
            model_name='project',
            name='media_files',
        ),
        migrations.AlterField(
            model_name='historicalproject',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0.0, message='Amount cannot be a negative value')]),
        ),
        migrations.AlterField(
            model_name='historicalproject',
            name='risk',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0.0, message='Risk cannot be a negative value'), django.core.validators.MaxValueValidator(1.0, message='Risk cannot be higher than 1.0')]),
        ),
        migrations.AlterField(
            model_name='project',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0.0, message='Amount cannot be a negative value')]),
        ),
        migrations.AlterField(
            model_name='project',
            name='risk',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0.0, message='Risk cannot be a negative value'), django.core.validators.MaxValueValidator(1.0, message='Risk cannot be higher than 1.0')]),
        ),
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together={('investor', 'project')},
        ),
        migrations.CreateModel(
            name='MediaFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_file', models.FileField(upload_to='project_files/')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_files', to='projects.project')),
            ],
        ),
    ]