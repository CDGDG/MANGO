from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
from .forms import LoginForm
# from .models import User

def base(request):
    return render(request, 'base.html')

def index(request):
    return render(request, 'index.html')

def elements(request):
    return render(request, 'elements.html')

def generic(request):
    return render(request, 'generic.html')
    

def myinfo(reqeust):
    pass

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
                request.session['user'] = user.id  
                return redirect('/user/index/')   # 로그인 성공후 home 으로 redirect
            else:
                # 비밀번호 불일치.  로그인 실패 처리
                res_data['error'] = '비밀번호를 틀렸습니다'

        return render(request, 'login.html', res_data)

def logout(request):
    pass