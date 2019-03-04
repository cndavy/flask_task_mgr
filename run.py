import os
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

import config
from admin import admin
from models import db
from views import app


app.config.from_object(config)
migrate = Migrate(app,db)
manager = Manager(app)
manager.add_command('db', MigrateCommand) # 在命令行中，用`db`调用`MigrateCommand`
app.register_blueprint(admin)
if __name__ == '__main__':
    os.system('cd %s' % os.path.abspath())
    manager.run()