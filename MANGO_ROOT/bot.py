import random
from tabnanny import verbose
import threading
import json

from bs4 import BeautifulSoup
import requests


from config.DatabaseConfig import *
from utils.Database import Database
from utils.BotServer import BotServer
from utils.Preprocess import Preprocess
from models.intent.IntentModel import IntentModel
from models.ner.NerModel import NerModel
from models.mood.LyricModel import LyricModel
from models.weather.WeatherModel import WeatherModel
from models.emotion.EmotionModel import EmotionModel
from utils.FindAnswer import FindAnswer
import os
import pandas as pd


# 전처리 객체 생성
intent_p = Preprocess(word2index_dic=os.path.abspath('train_tools/dict/chatbot_dictionary.bin'), userdic=os.path.abspath('utils/mango_dict_total.txt'))

lyric_p = Preprocess(word2index_dic=os.path.abspath('./train_tools/dict/lyric_dict.bin'))

ner_p = Preprocess(word2index_dic=os.path.abspath('./train_tools/dict/ner_dictionary.bin'), userdic=os.path.abspath('utils/mango_dic_ner.txt'))

weather_p = Preprocess(word2index_dic=os.path.abspath('./train_tools/dict/chatbot_dict.bin'), userdic=os.path.abspath('utils/weather2.txt'))

emotion_p = Preprocess(word2index_dic=os.path.abspath('./train_tools/dict/chatbot_dict.bin'))

# 의도 파악 모델
intent = IntentModel(model_name='models/intent/intent_model.h5', preprocess=intent_p)

# 개체명 인식 모델
ner = NerModel(model_name='models/ner/ner_model_shuffle.h5', preprocess=ner_p)

# 가사 분석 모델
mood = LyricModel(model_name='models/mood/lyric_model.h5', preprocess=lyric_p)

# 날씨 분석 모델
weather = WeatherModel(model_name='models/weather/weather_model.h5', preprocess=weather_p)

# 감정 의도 분석 모델
emotion = EmotionModel(model_name='models/emotion/emotion_model(7).h5', preprocess=emotion_p)

# 클라이언트 요청을 수행하는 함수 (쓰레드에 담겨 실행될거임)
def to_client(conn, addr, params):
    db = params['db']
    
    try:
        db.connect() # DB 연결
        
        # 데이터 수신 (클라이언트로부터 데이터를 받기 위함)
        # conn 은 챗봇 클라이언트 소켓 객체 ( 이 객체를 통해 클라이언트 데이터 주고 받는다 )
        read = conn.recv(131072)  # recv() 는 수신 데이터가 있을 때 까지 블로킹, 최대 2048 바이트만큼 수신
                                # 클라이언트 연결이 끊어지거나 오류발생시 블로킹 해제되고 None 리턴
        print('=== ' * 30)
        print('Connection from: %s' % str(addr))
        
        if read is None or not read:
            # 클라이언트 연결이 끊어지거나, 오류가 있는 경우
            print('클라이언트 연결 끊어짐')
            exit(0) # 종료
            
        # 수신된 데이터(json) 을 파이썬 객체로 변환
        recv_json_data = json.loads(read.decode())
        print('데이터 수신 :', recv_json_data['Query'])
        query = recv_json_data['Query']
        
        send_json_data_str = {}

        # 의도 파악
        intent_predict = intent.predict_class(query)
        intent_name = intent.labels[intent_predict]
        print('의도:', intent_name)

        emotion_predict = emotion.predict_class(query)
        emotion_name = emotion.labels[emotion_predict]

        if intent_predict == 0:
            print('감정의도:', emotion_name)
            emotion_name = {'혐오': '차분', '중립': '편안', '놀람':'잔잔', '공포': '편안'}.get(emotion_name, emotion_name)
            send_json_data_str['recommend'] = json.dumps(get_recommend_track(emotion_name), ensure_ascii=False)


        # 취향 추천
        mood_name = None
        if intent_predict == 10:
            # 사용자의 플레이리스트를 받아와야함..
            moodslist = []
            playlist = recv_json_data['Playlist']
            # 플레이리스트 취향 분석
            for lyric in [track['lyrics'] for track in playlist.values()]:
                moodslist.append(mood.predict_mood(lyric))
            # 그래프 만들기
            pd.DataFrame([[i, moodslist.count(i)] for i in mood.labels]).set_index(0)[1]
            # 음악 추천
            most_mood = max(moodslist, key=moodslist.count)
            if most_mood:
                send_json_data_str['recommend'] = json.dumps(get_recommend_track(most_mood), ensure_ascii=False)
            send_json_data_str['most_mood'] = most_mood

            
        # 개체명 파악
        ner_predicts = ner.predict(query)
        ner_tags = ner.predict_tags(query)
        print('개체명: ', ner_predicts, ner_tags)
        ner_track = None
        for ne in ner_predicts:
            if ne[1] == 'B_TRACK':
                ner_track = ne[0]
        print('트랙: ', ner_track)

        # 날씨 개체명 인식
        weather_predicts = None
        weather_tags = None
        ner_weather = None
        if intent_predict == 8:
            weather_predicts = weather.predict(query)
            weather_tags = weather.predict_tags(query)
            print('날씨개체명: ', weather_predicts, weather_tags)
            ner_weather = None
            for we in weather_predicts:
                if we[1] == 'B_WEATHER':
                    ner_weather = we[0]
            # 날씨로 음악 추천
            weather_dic = {'맑': '맑음', '흐리': '흐림',}
            ner_weather = weather_dic.get(ner_weather, ner_weather)
            if ner_weather:
                send_json_data_str['recommend'] = json.dumps(get_recommend_track(ner_weather), ensure_ascii=False)
            print('날씨: ',ner_weather)

        # 답변 검색, 분석된 의도와 개체명을 이용해 학습 DB 에서 답변을 검색
        fail = False
        try:
            f = FindAnswer(db)
            answer_text = f.search(intent_predict, ner_tags, weather_tags)
            answer = f.tag_to_word(intent_predict, ner_predicts, answer_text, weather_predicts, emotion_name)
            if 'B_TRACK' in answer or 'B_WEATHER' in answer or 'B_TIME' in answer:
                raise Exception
        except Exception as e:
            print(e)
            answer = "무슨 말인지 모르겠어요..<br>망고 봇에게 무엇을 요청하셨나요?"
            fail = True



        print('대답:', answer)

        # 검색된 답변데이터와 함께 앞서 정의한 응답하는 JSON 으로 생성
        send_json_data_str['Answer'] = answer
        send_json_data_str['Intent'] = intent_name
        send_json_data_str['NER'] = str(ner_predicts)
        send_json_data_str['TRACK'] = ner_track
        send_json_data_str['Weather'] = ner_weather
        send_json_data_str['Fail'] = fail
        send_json_data_str['emotion'] = emotion_name
        # send_json_data_str = {
        #     # 'Emotion': emotion,
        #     'Answer': answer,
        #     'AnswerImageUrl': answer_image,
        #     'Intent': intent_name,
        #     'NER': str(ner_predicts),
        # }

        # json 텍스트로 변환. 하여 전송
        message = json.dumps(send_json_data_str, ensure_ascii=False)
        conn.send(message.encode())

        
    except Exception as ex:
        print(ex)
        
    finally:
        if db is not None: # DB 연결 끊기
            db.close()
        conn.close()
            
    # 함수가 종료되면 쓰레드도 끝남

def get_recommend_track(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }

    url = 'https://www.melon.com/dj/djfinder/djfinder_inform.htm?djSearchType=P&djSearchKeyword='+query

    playlist_urls = ["https://www.melon.com/mymusic/dj/mymusicdjplaylistview_inform.htm?plylstSeq=" + btn['data-djcol-no'] for btn in BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser').select('#djPlylstList button.btn_djplylst_like')]

    playlist = playlist_urls[random.randint(0, len(playlist_urls)-1)]

    tracks = BeautifulSoup(requests.get(playlist, headers=headers).text, 'html.parser').select('div#pageList table tbody tr')
    song = tracks[random.randint(0, len(tracks)-1)]
    track = {
            'image': song.select_one(' div.wrap a.image_typeAll > img')['src'],
            'title': song.select_one(' div.wrap div.wrap_song_info .rank01 a').text.strip(),
            'artists': song.select_one(' div.wrap div.wrap_song_info .rank02 a').text.strip(),
            'url': "https://www.melon.com/song/detail.htm?songId=" + song.select_one('div.wrap.t_right input')['value']
            }
    return track


if __name__ == '__main__':
    # 질문/답변 학습 디비 연결 객체 생성
    db = Database(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db_name=DB_NAME
    )
    print("DB 접속")

    port = 5050
    listen = 100
    
    # 봇 서버 동작
    bot = BotServer(port, listen)
    bot.create_sock()
    print('bot start')
    
    # 무한루프를 돌면서 챗봇 클라이언트의 요청(연결) 을 기다린다 (listening)
    while True:
        conn, addr = bot.ready_for_client() # 서버 연걸 요청이 서버에서 수락되면, 곧바로 챗봇 클라이언트 서비스 요청 처리하는 쓰레드 생성
        
        params = {
            "db": db
        }
        client = threading.Thread(target=to_client, args=(
            conn, # 클라이언트 연결 소켓
            addr, # 클라이언트 연결 주소 정보 
            params # 쓰레드 내부에서 DB 에 접근할 수 있도록 넘겨줌
        ))
        
        client.start() # 쓰레드 시작. 위 target 함수가 별도의 쓰레드에 실려 실행된다.