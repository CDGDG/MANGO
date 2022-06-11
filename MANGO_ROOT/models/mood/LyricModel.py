import tensorflow as tf
from tensorflow.keras.models import Model, load_model
from tensorflow.keras import preprocessing

# 의도 분류 모델 모듈
class LyricModel:
    def __init__(self, model_name, preprocess):

        # 의도 클래스 별 레이블
        self.labels = ['신남', '힐링', '짝사랑', '센치', '위로', '슬픔', '사랑', '스트레스 해소']

        # 의도 분류 모델 불러오기
        self.model = load_model(model_name)

        # 챗봇 Preprocess 객체
        self.p = preprocess


    # 의도 클래스 예측
    def predict_class(self, query):
        # 형태소 분석
        pos = self.p.pos(query)

        # 문장내 키워드 추출(불용어 제거)
        keywords = self.p.get_keywords(pos, without_tag=True)
        sequences = [self.p.get_wordidx_sequence(keywords)]

        # 단어 시퀀스 벡터 크기
        MAX_SEQ_LEN = 10

        # 패딩처리
        padded_seqs = preprocessing.sequence.pad_sequences(sequences, maxlen=MAX_SEQ_LEN, padding='post')

        predict = self.model.predict(padded_seqs)
        predict_class = tf.math.argmax(predict, axis=1)
        return predict_class.numpy()[0]

    def predict_lyric(self, query):
        predict = self.predict_class(query)
        predict_label = self.labels[predict]

        return predict_label

    def predict_mood(self, lyric):
        data = [self.predict_lyric(l) for l in lyric.split('\n')]
        return max(data,key=data.count)