from flask_bootstrap import Bootstrap
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

import config
from models import db
from views import app


app.config.from_object(config)
migrate = Migrate(app,db)
manager = Manager(app)
manager.add_command('db', MigrateCommand) # 在命令行中，用`db`调用`MigrateCommand`

if __name__ == '__main__':
    manager.run()