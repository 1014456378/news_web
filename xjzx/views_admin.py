from flask import Blueprint, request, render_template, redirect, session, g, jsonify, current_app
from models import UserInfo, NewsCategory, db
from datetime import datetime

admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')


@admin_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('admin/login.html')
    # post请求，接收用户名、密码，进行验证，完成登录
    username = request.form.get('username')
    password = request.form.get('password')
    if not all([username, password]):
        return render_template('admin/login.html', msg='请输入用户名、密码')
    user = UserInfo.query.filter_by(mobile=username, isAdmin=True).first()
    if user:
        # 用户名正确
        # 判断密码是否正确
        if user.check_pwd(password):
            # 登录成功
            # 在session中记录管理员编号
            session['admin_user_id'] = user.id
            # 转到后台首页
            return redirect('/admin/')
        else:
            # 密码错误
            return render_template('admin/login.html', msg='密码错误')
    else:
        # 用户名错误
        return render_template('admin/login.html', msg='用户名错误')


# 注册为视图函数前的请求勾子
@admin_blueprint.before_request
def login_valid():
    # 判断是否为登录页，如果是则不执行验证
    page_list = ['/admin/login', ]
    # 通过请求路径，排除不需要执行验证的视图
    if request.path not in page_list:
        if 'admin_user_id' not in session:
            return redirect('/admin/login')
        g.user = UserInfo.query.get(session.get('admin_user_id'))


@admin_blueprint.route('/')
def index():
    # if 'admin_user_id' not in session:
    #     return redirect('/admin/login')
    # g.user=UserInfo.query.get(session.get('admin_user_id'))
    return render_template('admin/index.html')


@admin_blueprint.route('/logout')
def logout():
    del session['admin_user_id']
    return redirect('/admin/login')


@admin_blueprint.route('/user_list')
def user_list():
    return render_template('admin/user_list.html')


@admin_blueprint.route('/user_list_json')
def user_list_json():
    # 分页的数据列表
    page = int(request.args.get('page', '1'))
    pagination = UserInfo.query \
        .filter_by(isAdmin=False) \
        .order_by(UserInfo.id.desc()) \
        .paginate(page, 9, False)
    # 获取当前页数据
    user_list1 = pagination.items
    # 获取总页数
    total_page = pagination.pages

    # 将数据转成json格式
    user_list2 = []
    for user in user_list1:
        user_list2.append({
            'nick_name': user.nick_name,
            'mobile': user.mobile,
            'create_time': user.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': user.update_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    # 响应
    return jsonify(user_list=user_list2, total_page=total_page)


@admin_blueprint.route('/user_count')
def user_count():
    now = datetime.now()
    # 用户总数
    total = UserInfo.query.filter_by(isAdmin=False).count()
    # 用户月新增数
    # 本月第一天
    month_first = datetime(now.year, now.month, 1)
    total_month = UserInfo.query \
        .filter_by(isAdmin=False) \
        .filter(UserInfo.create_time >= month_first) \
        .count()
    # 用户日新增数
    day_first = datetime(now.year, now.month, now.day)
    total_day = UserInfo.query \
        .filter_by(isAdmin=False) \
        .filter(UserInfo.create_time >= day_first) \
        .count()

    # 查询每小时的登录数量
    # 获取登录的时间
    hour_list = current_app.redis_cli.hkeys(now.strftime('%Y-%m-%d'))
    # 获取登录的数量
    count_list = current_app.redis_cli.hvals(now.strftime('%Y-%m-%d'))

    # 将bytes类型转换成字符串和int
    hour_list2 = []
    for hour in hour_list:
        hour_list2.append(hour.decode())
    count_list2 = []
    for count in count_list:
        count_list2.append(int(count))
    # print(hour_list2)
    # print(count_list2)



    return render_template(
        'admin/user_count.html',
        total=total,
        total_month=total_month,
        total_day=total_day,
        hour_list2=hour_list2,
        count_list2=count_list2
    )


@admin_blueprint.route('/news_type')
def news_type():
    return render_template('admin/news_type.html')


@admin_blueprint.route('/news_type_json')
def news_type_json():
    type_list1 = NewsCategory.query.all()
    type_list2 = []
    for category in type_list1:
        type_list2.append({
            'id': category.id,
            'name': category.name
        })
    return jsonify(type_list=type_list2)


@admin_blueprint.route('/type_add_edit', methods=['POST'])
def type_add_edit():
    name = request.form.get('name')
    sid=request.form.get('sid')
    if not name:
        return jsonify(result=1)
    if NewsCategory.query.filter_by(name=name).count() > 0:
        return jsonify(result=2)
    if sid:
        #修改
        category=NewsCategory.query.get(sid)
        category.name=name
    else:
        # 增加
        category = NewsCategory()
        category.name = name
        db.session.add(category)
    #提交到数据库
    db.session.commit()
    #响应
    return jsonify(result=3,id=category.id)
