from gc import get_objects
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.hashers import make_password, check_password
import requests
import json
from bs4 import BeautifulSoup
from sympy import re
from .forms import LoginForm, JoinForm
from .models import Music_prefer, Playlist, User

def base(request):
    return render(request, 'base.html')

def index(request):
    return render(request, 'index.html')

def elements(request):
    return render(request, 'elements.html')

def generic(request):
    return render(request, 'generic.html')

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        userid = request.POST.get('userid', None)
        password = request.POST.get('password', None)

        res_data = {}

        if not(userid and password):  # 값이 다 입력되었는지 확인
            res_data['error'] = '모든 값을 입력해야 합니다'
        else:
            # 모델로부터 데이터를 가져와야 한다
            user = User.objects.get(userid=userid)
            # 비밀번호 비교
            if check_password(password, user.password):
                # 로그인 처리 (세션 사용)
                request.session['user'] = {'id': user.id, 'userid': user.userid}
                request.session['playlist'] = ",".join([track.youtube for track in Playlist.objects.filter(user=user).order_by('-id')])
                request.session['playlist_info'] = json.dumps({str(i):{'track': track.track, 'artist': track.artist, 'lyrics': track.lyrics} for i, track in enumerate(Playlist.objects.filter(user=user).order_by('-id'))}, ensure_ascii=False)
                return redirect('/')   # 로그인 성공후 home 으로 redirect
            else:
                # 비밀번호 불일치.  로그인 실패 처리
                res_data['error'] = '비밀번호를 틀렸습니다'

        return render(request, 'login.html', res_data)

def logout(request):
    if request.session.get('user'):
        del(request.session['user'])
    return redirect('/')

def join(request):
    # 회원가입 처리
    if request.method=="POST":
        form = JoinForm(request.POST)
        moods = ['슬픔', '감사', '걱정', '중립', '기쁨', '분노', '여유', '스트레스', '신남', '실망', '외로운', '우울함', '편안']
        if form.is_valid():
            user = User(
                userid = form.userid,
                password = make_password(form.password),
            )
            user.save()

            for pk in form.prefer:
                Music_prefer(
                    user=user,
                    preference=moods[int(pk)],
                ).save()
        else: 
            print("join 실패")
        return redirect("/user/login/")
    else:
        form = JoinForm()
        return render(request,'join.html',{'form':form})

def checkid(request):
    userid = request.GET.get('userid')
    context={}
    try:
        User.objects.get(userid=userid)
    except:
        context['data'] = "not exist" # 아이디 중복 없음

    return JsonResponse(context)

def addPlaylist(request):
    if request.session['user']:
        userid = request.session['user']['id']
    else:
        return JsonResponse({'data': 'nologin'})

    youtube = request.GET.get('youtube')
    track = request.GET.get('track')
    artist = request.GET.get('artist')
    lyrics = getLyrics(track, artist)

    play = Playlist(user=get_object_or_404(User, id=userid), youtube=youtube, track=track, artist=artist, lyrics=lyrics)
    play.save()
    request.session['playlist'] = ",".join([track.youtube for track in Playlist.objects.filter(user=userid).order_by('-id')])
    request.session['playlist_info'] = json.dumps({str(i):{"track": track.track, "artist": track.artist, "lyrics": track.lyrics} for i, track in enumerate(Playlist.objects.filter(user=userid).order_by('-id'))}, ensure_ascii=False)
    return JsonResponse({'data': request.session['playlist']})

def getLyrics(track, artist):
    track2 = track.replace('953964', '&amp;')
    query = f'{track2} {artist}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }
    q_url = 'https://www.melon.com/search/song/index.htm?q='+query
    try:
        trackid = BeautifulSoup(requests.get(q_url, headers=headers).text, 'html.parser').select_one('table tbody tr td div.wrap.pd_none.left input')['value']
        url = 'https://www.melon.com/song/popup/lyricPrint.htm?songId='+trackid
        temp_lyrics =  str(BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser').select_one('.box_lyric_text')).replace('<div class="box_lyric_text">', '').replace('</div>', '').replace('\r', '').replace('\n', '').replace('\t', '').split('<br/>')
    except Exception as e:
        return '가사 불러오기 실패'
    return "\n".join(temp_lyrics)

def getPlaylist(request):
    if request.session['user']:
        userid = request.session['user']['id']
    else:
        return JsonResponse({'data': 'nologin'})

    return JsonResponse({'playlist': ",".join([track.youtube for track in Playlist.objects.filter(user=userid).order_by('-id')])})

def showPlaylist(request):
    if request.session['user']:
        userid = request.session['user']['id']
    else:
        return JsonResponse({'data': 'nologin'})

    context = [
        {
            'youtube': play.youtube,
            'track': play.track,
            'artist': play.artist,
        }
        for play in Playlist.objects.filter(user=userid).order_by('-id')
    ]
    return JsonResponse({'playlist': context})

def deletePlaylist(request, track):
    if request.session['user']:
        userid = request.session['user']['id']
    cnt = False
    try:
        playlist = Playlist.objects.filter(user=userid).order_by('-id')
        for tr in playlist:
            if tr.track.replace(" ", "") == track.replace(" ", ""):
                tr.delete()
                cnt = True
        
        if cnt:
            return JsonResponse({'data': 'success'})
        else:
            return JsonResponse({'data': 'fail'})

    except Exception as e:
        return JsonResponse({'data': 'fail'})