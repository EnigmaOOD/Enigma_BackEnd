# Generated by Django 4.1.7 on 2023-05-05 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyUser', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
    ]
