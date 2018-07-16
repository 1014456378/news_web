from flask_script import Manager
import config
import app

flask_app = app.create(config.DevelopConfig)
manager = Manager(flask_app)
#添加迁移命令
from models import db
from flask_migrate import Migrate,MigrateCommand
migrate = Migrate(flask_app,db)
from super_command import CreateSuperUserCommant,CreateTestUser,CreateTestLogin
manager.add_command('createuser',CreateSuperUserCommant())
manager.add_command(('createtest'),CreateTestUser())
manager.add_command(('createlogin'),CreateTestLogin())

manager.add_command('db',MigrateCommand)

if __name__ == '__main__':
    manager.run()
