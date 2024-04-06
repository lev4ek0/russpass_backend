# Generated by Django 5.0.4 on 2024-04-06 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0003_alter_photo_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='extention',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='photo_extension'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='height',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='width',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]