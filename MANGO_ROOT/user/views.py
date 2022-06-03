from gc import get_objects
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.hashers import make_password, check_password
import requests
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

    play = Playlist(user=get_object_or_404(User, id=userid), youtube=youtube, track=track, artist=artist)
    play.save()
    request.session['playlist'] = ",".join([track.youtube for track in Playlist.objects.filter(user=userid).order_by('-id')])
    return JsonResponse({'data': request.session['playlist']})

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