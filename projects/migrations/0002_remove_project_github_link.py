# Generated by Django 5.1.3 on 2024-11-23 13:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='github_link',
        ),
    ]
