from django.db import models

class Chatbot(models.Model):
    intent = models.IntegerField(verbose_name='의도')
    emotion = models.IntegerField(verbose_name='감정', null=True)
    ner = models.CharField(max_length=100, null=True, verbose_name='개체명')
    answer = models.TextField(verbose_name='대답')
    answer_image = models.CharField(max_length=200, null=True, verbose_name='대답이미지')

    class Meta:
        db_table = 'mango_train_data'
        verbose_name = '챗봇'
        verbose_name_plural = '챗봇(들)'

