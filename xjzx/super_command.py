from flask_script.commands import Command

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