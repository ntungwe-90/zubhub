# Generated by Django 2.2.7 on 2020-11-25 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='video',
            field=models.URLField(max_length=1000),
        ),
    ]