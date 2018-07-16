function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {
    var sHandler = 'edit';
    var sId = 0;
    var $pop = $('.pop_con');
    var $input = $('.input_txt3');
    var $cancel = $('.cancel');
    var $confirm = $('.confirm');
    var $error = $('.error_tip');

    common_table_vue = new Vue({
        el: '.common_table',
        delimiters: ['[[', ']]'],
        data: {
            type_list: []
        },
        methods: {
            add: function () {
                sHandler = 'add';
                $pop.find('h3').html('新增分类');
                $input.val('');
                $pop.show();
            },
            edit: function (id, name) {
                sHandler = 'edit';
                sId = id;//$(this).parent().siblings().eq(0).html();
                $pop.find('h3').html('修改分类');
                // $pop.find('.input_txt3').val($(this).parent().prev().html());
                $pop.find('.input_txt3').val(name);
                $pop.show();
            }
        }
    });

    load_type();

    $cancel.click(function () {
        $pop.hide();
        $error.hide();
    });

    $input.click(function () {
        $error.hide();
    });

    $confirm.click(function () {
        var csrf_token = $('#csrf_token').val();
        if (sHandler == 'edit') {
            var sVal = $input.val();
            if (sVal == '') {
                $error.html('输入框不能为空').show();
                return;
            }
            $.post('/admin/type_add_edit', {
                'name': sVal,
                'csrf_token': csrf_token,
                'sid':sId
            }, function (data) {
                if (data.result == 1) {
                    $error.html('请填写名称').show();
                } else if (data.result == 2) {
                    $error.html('此名称已经存在').show();
                } else if (data.result == 3) {
                    $pop.hide();
                    $error.hide();
                    load_type();
                }
            });
        }
        else {
            var sVal = $input.val();
            if (sVal == '') {
                $error.html('输入框不能为空').show();
                return;
            }
            $.post('/admin/type_add_edit', {
                'name': sVal,
                'csrf_token': csrf_token
            }, function (data) {
                if (data.result == 1) {
                    $error.html('请填写名称').show();
                } else if (data.result == 2) {
                    $error.html('此名称已经存在').show();
                } else if (data.result == 3) {
                    $pop.hide();
                    $error.hide();
                    common_table_vue.type_list.push({
                        'id': data.id,
                        'name': sVal
                    })
                }
            });
        }

    })
})

function load_type() {
    $.get('/admin/news_type_json', function (data) {
        common_table_vue.type_list = data.type_list;
    });
}