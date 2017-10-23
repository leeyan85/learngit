function test(){
    var use = $("input[ type='text']").val();
    var pas = $("input[ type='password']").val();
    if(use){
    }else {
        $("input[type='text']").css("::-webkit-input-placeholder","rgba(255, 12, 0, 0.72)");
        $("input[type='text']").css("color","rgba(255, 12, 0, 0.72)");
    }
    if(pas){
    }else {
        $("input[type='password']").css("::-webkit-input-placeholder","rgba(255, 12, 0, 0.72)");
        $("input[type='password']").css("color","rgba(255, 12, 0, 0.72)");
    }
}
function test2(){
    $("input[type='text']").css("color","#fff");
    $("input[type='password']").css("color","#fff");
}

function validate(){
    var name = $("input[ name='username']").val();
    var pass = $("input[ name='password']").val();
    $.ajax({
        type:"POST",
        url:"/accounts/login/",
        data:{username:name, password:pass},
        success:function(datas){
            var dd = eval("("+datas+")");
            if (dd.status =='failed'){
               alert("用户名或密码错误");            
            } else {
               location.href="/home/" 
            }
        },
        error:function(){
            alert("提交异常");
        }
    })
}

