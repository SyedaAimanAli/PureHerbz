# Generated by Django 5.1.3 on 2024-11-22 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_review'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='rating',
        ),
    ]
