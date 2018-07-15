from flask import Blueprint, jsonify
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from models import UserInfo

admin_blueprint = Blueprint('admin',__name__,url_prefix='/admin')

@admin_blueprint.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('admin/login.html')
    username=request.form.get('username')
    password=request.form.get('password')
    if not all([username,password]):
        return render_template('admin/login.html',msg = '请输入用户名和密码')
    user=UserInfo.query.filter_by(mobile=username,isAdmin=True).first()
    if user:
        if user.check_pwd(password):
            session['admin_user_id']=user.id
            return redirect('/admin/')
        else:
            return render_template('admin/login.html',msg='密码错误')

    else:
        return render_template('admin/login.html',msg='用户名错误')

@admin_blueprint.before_request
def login_valid():
    page_list=['/admin/login',]
    if request.path not in page_list:
        if 'admin_user_id' not in session:
            return redirect('/admin/login')
        g.user = UserInfo.query.get(session.get('admin_user_id'))


@admin_blueprint.route('/')
def index():
    if 'admin_user_id' not in session:
        return redirect('/admin/login')
    g.user=UserInfo.query.get(session.get('admin_user_id'))
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
    page=int(request.args.get('page','1'))
    pagination=UserInfo.query.filter_by(isAdmin=False).order_by(UserInfo.id.desc()).paginate(page,9,False)
    user_list1=pagination.items
    total_page=pagination.pages
    user_list2=[]
    for user in user_list1:
        user_list2.append(
            {
                'nick_name':user.nick_name,
                'mobile':user.mobile,
                'create_time':user.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'update_time':user.update_time.strftime('%Y-%m-%d %H:%M:%S')

        }
        )
    return jsonify(user_list=user_list2,total_page=total_page)


