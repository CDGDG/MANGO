$(function(){
    // SEND 버튼을 누르거나
    $('#sendbtn').click(function(){
        send_message();
    })

    // ENTER key 가 눌리면
    $("#chattext").keyup(function(event){
        if(event.keyCode == 13){
            send_message();
        }
    })
})
function send_message(){
    const chattext = $('#chattext').val().trim()

    // 입력한 메세지가 없으면 리턴
    if(chattext == ""){
        $("#chattext").focus();
        return;
    }

    // 입력한 채팅 화면에 출력
    const addtext = "<div style='margin:2% 0%;text-align:right;'><span style='padding:1% 2%;background-color:#ff8b77;border-radius:10px;color:white;display:inline-block'>" + 
        (chattext.length>15?chattext.split('').reduce((acc,cur,i)=>{
            return acc+cur+(i%15==0?"<br>":"")
        }) :chattext)  + "</span></div>";
    $("#chatbox").append(addtext);

    // 먼저 입력했던 것은 지우기
    $('#chattext').val("");
    $('#chattext').focus();

    // API 서버에 요청할 데이터
    const jsonData = {
        query: chattext
    }

    $.ajax({
        url: 'http://127.0.0.10:5000/query/MANGO',
        type: "POST",
        data: JSON.stringify(jsonData),
        dataType: 'JSON', // 응답받을 데이터 타입
        contentType: 'application/json; charset=utf-8',

        success: function(response){
            // response.Answer 에 담겨있다.
    
            $chatbox = $('#chatbox');

            answerText = (response.Answer.length>15?response.Answer.split('').reduce((acc,cur,i)=>{
                return acc+cur+(i%15==0?"<br>":"")
            }) :response.Answer)

            // 답변출력
            const bottext = "<div style='margin:2% 0%;text-align:left;'><span style='padding:1% 2%;background-color:#ffcd48;border-radius:10px;color:#424242;display:inline-block'><b>" + 
                answerText + "</b></span></div>";
            $chatbox.append(bottext);

            // 스크롤 조정하기
            $chatbox.animate({scrollTop: $chatbox.prop('scrollHeight')})

            // 챗봇 동작
            if(response.Intent == '재생목록 재생'){
                ajax
                $('#player').src = 'https://www.youtube.com/embed?playlist='+request.session.playlist+'&autoplay=1&loop=1'
            }
        }
    })
}