# Generated by Django 5.1.3 on 2024-11-19 08:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_alter_userprofile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('category', models.CharField(choices=[('food', 'Food'), ('cars', 'Cars'), ('art', 'Art'), ('musique', 'Musique'), ('games', 'Games'), ('fashion', 'Fashion')], max_length=10)),
                ('description', models.TextField()),
                ('goal_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('raised_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('github_link', models.URLField(blank=True, null=True)),
                ('website_link', models.URLField(blank=True, null=True)),
                ('isActive', models.BooleanField(default=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='users.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Investment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('investor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='investments', to='users.userprofile')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='investments', to='projects.project')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='photo/project/')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image', to='projects.project')),
            ],
        ),
        migrations.CreateModel(
            name='Commentary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='photo/commentary/')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='users.userprofile')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='projects.project')),
            ],
        ),
    ]
