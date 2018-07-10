from flask import Blueprint, jsonify
from flask import g
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from models import UserInfo, db, NewsCategory,NewsInfo
from utils.ytx_sdk import ytx_send
from utils.captcha.captcha import captcha
import random
import functools
from utils import qiniu_upload
user_blueprint = Blueprint('user',__name__,url_prefix='/user')

@user_blueprint.route('/image_code')
def image_code():
    #生成图片验证码
    name,text,image = captcha.generate_captcha()
    response = make_response(image)
    #文件标准，告诉前端是啥类型的
    response.mimetype = 'image/png'
    # 验证码的文本
    print(text)
    session['image_code'] = text
    return response

@user_blueprint.route('/sms_code')
def sms_code():
    #接受图片验证码后发送短信
    image_code_request = request.args.get('image_code')
    image_code_session = session.get('image_code')
    if image_code_request!=image_code_session:
        return jsonify(result = 1)

    mobile = request.args.get('mobile')
    code = random.randint(1000,9999)
    session['sms_code'] = code
    session['mobile'] = mobile
    print(code)
    #调用云通讯发送短信
    # ytx_send.sendTemplateSMS('手机号',['过期时间','验证码'],'模板编号')
    # ytx_send.sendTemplateSMS(mobile,['5','%s' %code],1)
    return jsonify(result = 0)

@user_blueprint.route('/register',methods =['POST'])
def register():
    form = request.form
    mobile = form.get('mobile')
    sms_code = form.get('sms_code')
    pwd = form.get('pwd')
    if not all([mobile,sms_code,pwd]):
        return jsonify(result = 1) #参数有空
    sms_code_session = str(session.get('sms_code'))
    if sms_code!=sms_code_session:
        return jsonify(result = 2)#短信验证码错误
    mobile_exists = UserInfo.query.filter_by(mobile = mobile).count()
    if mobile_exists:
        return jsonify(result = 3)#手机号存在
    if mobile != session.get('mobile'):
        return jsonify(result = 4)#两次手机号不一致
    user = UserInfo()
    user.nick_name = mobile
    user.mobile = mobile
    user.password = pwd
    db.session.add(user)
    db.session.commit()
    return jsonify(result = 0)#成功

@user_blueprint.route('/login',methods = ['POST'])
def login():
    mobile = request.form.get('mobile')
    pwd = request.form.get('pwd')
    if not all([mobile,pwd]):
        return jsonify(result = 1)#数据不完整
    user = UserInfo.query.filter_by(mobile = mobile).first()
    if user:
        if user.check_pwd(pwd):
            #记录用户登录
            session['user_id'] = user.id
            #返回头像和昵称
            return jsonify(result = 0,nick_name = user.nick_name,avatar = user.avatar)
        else:
            return jsonify(result = 4) #密码错误
    else:
        return jsonify(result = 2)  #手机号错误

@user_blueprint.route('/logout',methods = ['POST'])
def logout():
    session.pop('user_id')
    return jsonify(result = 1)

#装饰器验证用户登录
def required_login(view_fun):
    @functools.wraps(view_fun)
    def fun1(*args,**kwargs):
        if 'user_id' not in session:
            return redirect('/')
        g.user = UserInfo.query.get(session['user_id'])
        return view_fun(*args,**kwargs)
    return fun1

@user_blueprint.route('/')
@required_login
def index():
    user = g.user
    title = '用户中心'
    return render_template('/news/user.html',user = user,title = title)

@user_blueprint.route('/base',methods = ['GET','POST'])
@required_login
def base():
    user = g.user
    if request.method =='GET':
        return render_template('news/user_base_info.html',user = user)
    signature = request.form.get('signature')
    nick_name = request.form.get('nick_name')
    gender = bool(int(request.form.get('gender')))
    user.signature = signature
    user.nick_name = nick_name
    user.gender = gender
    db.session.commit()
    return jsonify(result = 0)

@user_blueprint.route('/pic',methods = ['get','POST'])
@required_login
def pic():
    if request.method =='GET':
        return render_template('news/user_pic_info.html')
    avatar=request.files.get('avatar')
    if not avatar:
        return jsonify(result = 1)
    avatar_name = qiniu_upload.upload(avatar)
    user=g.user
    user.avatar = avatar_name
    db.session.commit()
    return jsonify(result = 2,avatar=user.avatar_url)
@user_blueprint.route('/follow')
@required_login
def follow():
    user = g.user
    author_list = user.authors
    page = int(request.args.get('page','1'))
    pagination = author_list.paginate(page,4,False)
    author_items = pagination.items
    #总页数
    total_page = pagination.pages
    return render_template('news/user_follow.html',author_items=author_items,total_page=total_page,page = page)
@user_blueprint.route('/pass',methods = ['GET','POST'])
@required_login
def pwd():
    if request.method == 'GET':
        return render_template('news/user_pass_info.html',msg = '')
    pwd1 = request.form.get('pwd1')
    pwd2 = request.form.get('pwd2')
    pwd3 = request.form.get('pwd3')
    if not all([pwd1,pwd2,pwd3]):
        return render_template('news/user_pass_info.html',msg = '数据不能为空')
    if len(pwd1)<6:
        return render_template('news/user_pass_info.html',msg = '旧密码错误')
    if len(pwd2)<6:
        return render_template('news/user_pass_info.html', msg='新密码长度不能小于6位')
    if pwd2 != pwd3:
        return render_template('news/user_pass_info.html',msg = '两个新密码不一致')
    user = g.user
    if user.check_pwd(pwd1):
        user.password=pwd2
        db.session.commit()
        return render_template('news/user_pass_info.html',msg = '修改成功')

    else:
        return render_template('news/user_pass_info.html',msg = '旧密码错误')

@user_blueprint.route('/collection')
@required_login
def collection():
    user = g.user
    news_list = user.news_collect
    page = int(request.args.get('page','1'))
    pagination = news_list.paginate(page,6,False)
    news_items = pagination.items
    tatal_page = pagination.pages
    return render_template('news/user_collection.html',news_items=news_items,tatal_page=tatal_page,page=page)
@user_blueprint.route('/release',methods = ['GET','POST'])
@required_login
def release():
    if request.method=='GET':
        category_list=NewsCategory.query.all()
        return render_template('news/user_news_release.html',category_list=category_list)
    title = request.form.get('title')
    category = request.form.get('category')
    summary = request.form.get('summary')
    content = request.form.get('content')
    if not all([title,category,summary,content]):
        return '请填写完整数据'
    news = NewsInfo()
    news.title=title
    news.category_id=category
    news.summary = summary
    news.context = content
    pic = request.files.get('pic')
    pic_name=qiniu_upload.upload(pic)
    news.pic=pic_name
    news.user_id=session.get('user_id')
    db.session.add(news)
    db.session.commit()
    return redirect('/user/list')


@user_blueprint.route('/list')
@required_login
def news_list():
    page = int(request.args.get('page',1))
    pagination = g.user.news.order_by(NewsInfo.id.desc()).paginate(page,6,False)
    news_list1 = pagination.items
    total_page = pagination.pages
    return render_template('news/user_news_list.html',news_list1 = news_list1,total_page = total_page,page=page)

@user_blueprint.route('/edit/<int:news_id>',methods=['GET','POST'])
@required_login
def edit(news_id):
    news=NewsInfo.query.get(news_id)
    if request.method=='GET':
        category_list=NewsCategory.query.all()
        return render_template('news/user_news_edit.html',category_list=category_list,news=news)
    title = request.form.get('title')
    category = request.form.get('category')
    summary = request.form.get('summary')
    content = request.form.get('content')
    if not all([title, category, summary, content]):
        return '请填写完整数据'
    news.title = title
    news.category_id = category
    news.summary = summary
    news.context = content
    pic = request.files.get('pic')
    if pic:
        pic_name = qiniu_upload.upload(pic)
        news.pic = pic_name
    news.user_id = session.get('user_id')
    news.status=1
    db.session.commit()
    return redirect('/user/list')