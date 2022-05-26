from django import forms
from user.models import User

class LoginForm(forms.Form):
    userid = forms.CharField(
        error_messages={
            'required' : '아이디를 입력해주세요'
        },
        max_length=20,label='아이디'
    )
    password = forms.CharField(
        error_messages={
            'required' : '비밀번호를 입력해주세요'
        },
        widget=forms.PasswordInput,max_length=100,label='비밀번호'
    )


    def clean(self):
        cleaned_data = super().clean()

        self.userid = cleaned_data.get('userid')
        self.password = cleaned_data.get('password')

class JoinForm(forms.ModelForm):
    password = forms.CharField(
        error_messages={
            'required' : '비밀번호를 입력해주세요'
        },
        widget=forms.PasswordInput,max_length=500,label='비밀번호'
    )

    re_password = forms.CharField(
        error_messages={
            'required' : '비밀번호를 입력해주세요'
        },
        widget=forms.PasswordInput,max_length=500,label='비밀번호 확인'
    )

    # 취향
    prefer = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=enumerate(['슬픔', '감사', '걱정', '중립', '기쁨', '분노', '여유', '스트레스', '신남', '실망',
       '외로운', '우울함', '편안']), label='음악 취향')
    
    class Meta:
        model = User
        fields = '__all__'

    def clean(self):   
        # 우선 부모 Form 의 clean() 수행 --> 값이 들어있지 않으면 error 처리 
        cleand_data = super().clean()
        
        self.userid = cleand_data.get('userid')
        self.password = cleand_data.get('password')
        self.prefer = cleand_data.get('prefer')