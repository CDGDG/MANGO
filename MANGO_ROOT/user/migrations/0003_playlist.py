# Generated by Django 3.2.5 on 2022-06-01 06:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20220526_0014'),
    ]

    operations = [
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('song_num', models.IntegerField(default=0, verbose_name='곡 번호')),
                ('order', models.IntegerField(default=0, verbose_name='곡 순서')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
            options={
                'verbose_name': '플레이리스트',
                'verbose_name_plural': '플레이리스트(들)',
                'db_table': 'MANGO_playlist',
            },
        ),
    ]