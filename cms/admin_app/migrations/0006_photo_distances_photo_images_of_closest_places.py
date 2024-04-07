# Generated by Django 5.0.4 on 2024-04-07 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0005_photo_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='distances',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='images_of_closest_places',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
