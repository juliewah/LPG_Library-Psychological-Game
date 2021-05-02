# Generated by Django 3.2 on 2021-04-30 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0026_pointrecord_typeof'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pointrecord',
            name='typeof',
            field=models.IntegerField(choices=[(1, '測驗推薦書'), (2, '其他書'), (3, '推薦書籍'), (4, '分享')], default=1, max_length=10, verbose_name='類型'),
        ),
    ]
