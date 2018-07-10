function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $('.pic_info').submit(function (e) {
        e.preventDefault()

        //使用jquery.form完成文件的ajax上传
        $(this).ajaxSubmit({//使用表单对象调用ajaxSubmit方法，用于上传图片，并且局部刷新
            url: "/user/pic",//请求的地址
            type: "post",//请求方式为post
            dataType: "json",//返回值的类型为json
            success: function (data) {//服务器返回200时的处理函数
                if (data.result == 2) {
                    //更新img标签中的图片
                    $('.now_user_pic').attr('src',data.avatar);
                    //更新左侧头像
                    $('.user_center_pic img',parent.document).attr('src',data.avatar);
                    //更新右上角头像
                    $('.lgin_pic',parent.document).attr('src',data.avatar);
                } else {
                    alert('文件上传失败，请稍候重试');
                }
            }
        });
    });
})