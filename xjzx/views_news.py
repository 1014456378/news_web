from flask import Blueprint,render_template

news_blueprint = Blueprint('news', __name__)


@news_blueprint.route('/')
def index():
    return render_template('news/index.html')

# #浏览器会自动请求一个地址，名称为'/favicon.ico'
# @news_blueprint.route('/favicon.ico')
# def ico():
#     #到静态文件夹static中查找指定的静态文件
#     return news_blueprint.send_static_file('/static/news/images/favicon.ico')
