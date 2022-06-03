from django.db import models

class User(models.Model):
    userid = models.CharField(max_length=20, verbose_name='아이디')
    password = models.CharField(max_length=500, verbose_name='비밀번호')

    class Meta:
        db_table = 'MANGO_user'
        verbose_name = '유저'
        verbose_name_plural = '유저(들)'

    def __str__(self):
        return f'id{self.id}.{self.userid}'

class Music_prefer(models.Model):
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    preference = models.CharField(max_length=50, verbose_name='음악 분위기')

    class Meta:
        db_table = 'MANGO_music_prefer'
        verbose_name = '선호 음악 분위기'
        verbose_name_plural = '선호 음악 분위기(들)'


# class Like_song(models.Model):
#     userpk = models.ForeignKey('user.User', on_delete=models.CASCADE)
#     song_num = models.IntegerField(verbose_name='곡 번호')

#     class Meta:
#         db_table = 'MANGO_like_song'

class Playlist(models.Model):
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    youtube = models.CharField(max_length=200, verbose_name='유튜브url')
    track = models.CharField(max_length=200, verbose_name='제목')
    artist = models.CharField(max_length=200, verbose_name='아티스트')
    order = models.IntegerField(default=0, verbose_name = '곡 순서')

    class Meta:
        db_table = 'MANGO_playlist'
        verbose_name = '플레이리스트'
        verbose_name_plural = '플레이리스트(들)'

    def __str__(self):
        return self.user.userid + '의 곡'
