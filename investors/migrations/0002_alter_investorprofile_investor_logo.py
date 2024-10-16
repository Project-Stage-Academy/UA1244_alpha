from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investorprofile',
            name='investor_logo',
            field=models.ImageField(blank=True, null=True, upload_to='investor_logos/'),
        ),
    ]
