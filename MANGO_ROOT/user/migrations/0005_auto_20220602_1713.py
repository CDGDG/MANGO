# Generated by Django 3.2.5 on 2022-06-02 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20220601_1609'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='artist',
            field=models.CharField(default=None, max_length=200, verbose_name='아티스트'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='playlist',
            name='youtube',
            field=models.CharField(default=None, max_length=200, verbose_name='유튜브url'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='playlist',
            name='track',
            field=models.CharField(max_length=200, verbose_name='제목'),
        ),
    ]
