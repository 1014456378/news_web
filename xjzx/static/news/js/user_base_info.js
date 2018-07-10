function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {

    $(".base_info").submit(function (e) {
        e.preventDefault()

        var signature = $("#signature").val()
        var nick_name = $("#nick_name").val()
        var gender = $(".gender").val()


        if (!gender) {
            alert('请选择性别')
        }

        // TODO 修改用户信息接口
        $.post('/user/base',{
            'signature':signature,
            'nick_name':nick_name,
            'gender':gender,
            'csrf_token':$('#csrf_token').val()},
            function (data) {
            if(data.result==0){
                //修改左侧昵称     要在父窗口拿到标签修改数据
                $('.user_center_name',parent.document).text(nick_name)
                //修改右上角的昵称
                $('#nick_name',parent.document).text(nick_name)

            }
        })
    })
})