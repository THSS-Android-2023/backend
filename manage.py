import os
import datetime

from flask_script import Manager
# from flask_migrate import Migrate, MigrateCommand

from app import create_app, db


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

# migrate = Migrate(app, db)
# manager.add_command('db', MigrateCommand)


@manager.command
def init_db():
    """Init db"""
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    print('ss')
    manager.run()