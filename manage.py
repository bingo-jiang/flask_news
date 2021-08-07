from project import create_app
from project.models import db
from flask_script import Manager,Server
from flask_migrate import Migrate, MigrateCommand

# app = create_app('develop')
app = create_app('product')
'''
1.创建Manage对象，管理app
2.使用Manger关联db和app
3.添加操作命令
'''
manager = Manager(app)
Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand)
# manager.add_command("runserver", Server("0.0.0.0", port=8080))
if __name__ == '__main__':
    manager.run()
