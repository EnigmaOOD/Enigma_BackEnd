# Generated by Django 4.1.7 on 2023-04-18 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Group', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
