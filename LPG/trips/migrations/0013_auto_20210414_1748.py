# Generated by Django 3.2 on 2021-04-14 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0012_auto_20210413_0111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booklist',
            name='ISBN',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AlterField(
            model_name='pointrecord',
            name='ISBN',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
    ]