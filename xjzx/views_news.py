from flask import Blueprint,render_template, jsonify
from flask import current_app
from flask import g
from flask import request
from flask import session

from models import NewsCategory,NewsInfo,UserInfo, db, NewsComment

news_blueprint = Blueprint('news', __name__)


@news_blueprint.route('/')
def index():
    category_list = NewsCategory.query.all()
    click_list = NewsInfo.query.order_by(
        NewsInfo.click_count.desc())[0:6]
    if 'user_id' in session:
        g.user=UserInfo.query.get(session.get('user_id'))
    else:
        g.user = None
    return render_template('news/index.html',category_list=category_list,click_list=click_list)

# #浏览器会自动请求一个地址，名称为'/favicon.ico'
# @news_blueprint.route('/favicon.ico')
# def ico():
#     #到静态文件夹static中查找指定的静态文件
#     return news_blueprint.send_static_file('/static/news/images/favicon.ico')

@news_blueprint.route('/list/<int:category_id>')
def news_list(category_id):
    # 返回json格式的新闻数据
    # 查询制定分类的新闻数据
    list1 = NewsInfo.query
    if category_id>0:
        #0表示最新的所有分类的新闻
        list1 = list1.filter_by(category_id = category_id)
    list1 = list1.order_by(NewsInfo.id.desc())
    page = int(request.args.get('page','1'))
    pagination = list1.paginate(page,4,False)
    list2 = pagination.items
    total_page = pagination.pages
    list3 =[]
    for news in list2:
        list3.append({
            'id': news.id,
            'pic_url': news.pic_url,
            'title': news.title,
            'summary': news.summary,
            'create_time': news.create_time.strftime('%Y-%m-%d'),
            'avatar': news.user.avatar_url,
            'nick_name': news.user.nick_name
        })
    return jsonify(list3 = list3,total_page = total_page)
@news_blueprint.route('/<int:news_id>')
def detail(news_id):
    news = NewsInfo.query.get(news_id)
    news.click_count+=1
    db.session.commit()
    if 'user_id' in session:
        g.user=UserInfo.query.get(session.get('user_id'))
    else:
        g.user=None
    click_list=NewsInfo.query.order_by(NewsInfo.click_count.desc())[0:6]

    return render_template('news/detail.html',news=news,click_list = click_list,title='文章详情页')
@news_blueprint.route('/comment_add',methods=['POST'])
def comment_add():
    msg = request.form.get('msg')
    news_id = request.form.get('news_id')
    comment_id=request.form.get('comment_id','0')
    if 'user_id' not in session:
        return jsonify(result=1)
    if not all([msg,news_id]):
        return jsonify(result = 2)
    try:
        news_id = int(news_id)
    except:
        return jsonify(result = 3)
    comment=NewsComment()
    comment.msg=msg
    comment.news_id=news_id
    comment.user_id=session.get('user_id')
    if comment_id!='0':
        comment.comment_id=int(comment_id)
    db.session.add(comment)
    news = NewsInfo.query.get(news_id)
    news.comment_count+=1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger_xjzx.error('添加评论数据库错误')
        return jsonify(result=5)
    return jsonify(result = 4)
@news_blueprint.route('/comment_list/<int:news_id>')
def comment_list(news_id):
    # 查询指定新闻的评论
    clist = NewsComment.query\
        .filter_by(news_id=news_id,comment_id=None)\
        .order_by(NewsComment.id.desc())
    # 将评论对象转成json对象
    clist2 = []
    count = 0
    for comment in clist:
        count += 1
        #获取评论的所有回复
        reply_list=[]
        for reply in comment.comments:
            reply_list.append({
                'id':reply.id,
                'msg':reply.msg,
                'nick_name':reply.user.nick_name
            })
        #构造评论对象
        clist2.append({
            'id': comment.id,
            'msg': comment.msg,
            'like_count': comment.like_count,
            'avatar_url': comment.user.avatar_url,
            'nick_name': comment.user.nick_name,
            'create_time': comment.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            #评论的所有回复
            'reply_list':reply_list
        })

    return jsonify(clist=clist2, count=count)

@news_blueprint.route('/collect',methods=['GET','POST'])
def collect():
    if request.method=='GET':
        news_id = request.args.get('news_id')
    else:
        news_id=request.form.get('news_id')
    flag=request.form.get('flag','1')
    if not news_id:
        return jsonify(result=1)
    if 'user_id' not in session:
        return  jsonify(result=2)
    user_id=session.get('user_id')
    news=NewsInfo.query.get(news_id)
    user=UserInfo.query.get(user_id)
    if not news:
        return jsonify(result=3)
    if request.method=='GET':
        if news in user.news_collect:
            return jsonify(result=4)
        else:
            return jsonify(result=5)
    if flag == '1':
        if news not in user.news_collect:
            user.news_collect.append(news)
        else:
            jsonify(result=5)
    else:
        if news in user.news_collect:
            user.news_collect.remove(news)
        else:
            jsonify(result=5)
    db.session.commit()
    return jsonify(result=4)


