from datetime import datetime
from flask import current_app
from flask_script.commands import Command
import random
from models import UserInfo, db


class CreateSuperUserCommant(Command):
    def run(self):
        username=input('请输入管理员账号:')
        pwd = input('请输入密码')
        user=UserInfo()
        user.mobile=username
        user.nick_name=username
        user.password=pwd
        user.isAdmin=True
        db.session.add(user)
        db.session.commit()
        print('创建管理员成功')

class CreateTestUser(Command):
    def run(self):
        user_list = []
        for i in range(100):
            user = UserInfo()
            user.nick_name = str(i)
            user.mobile = str(i)
            user.password = str(i)
            user.create_time = datetime(2018,random.randint(1,7),random.randint(1,16))
            user_list.append(user)
        db.session.add_all(user_list)
        db.session.commit()
        print('成功')

class CreateTestLogin(Command):
    def run(self):
        #将数据保存在Redis中
        #统计时间为：00:00---08:15-->19:15--23:59
        for i in range(8,20):
            current_app.redis_cli.hset('2018-07-16','%02d:00'%i,random.randint(100,999))
        print('登录数据完成')