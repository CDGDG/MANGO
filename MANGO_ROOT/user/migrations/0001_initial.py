from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userid', models.CharField(max_length=20, verbose_name='아이디')),
                ('password', models.CharField(max_length=500, verbose_name='비밀번호')),
            ],
            options={
                'verbose_name': '유저',
                'verbose_name_plural': '유저(들)',
                'db_table': 'MANGO_user',
            },
        ),
        migrations.CreateModel(
            name='Music_prefer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preference', models.CharField(max_length=50, verbose_name='음악 분위기')),
                ('userpk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
            options={
                'verbose_name': '선호 음악 분위기',
                'verbose_name_plural': '선호 음악 분위기(들)',
                'db_table': 'MANGO_music_prefer',
            },
        ),
        migrations.CreateModel(
            name='Like_song',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('song_num', models.IntegerField(verbose_name='곡 번호')),
                ('userpk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
            options={
                'db_table': 'MANGO_like_song',
            },
        ),
    ]
