import os
import json
import argparse

from sql.db_connect import Connect
from passlib.apps import custom_app_context as pwd_context

class UserUtils():
    def __init__(self):

        with open(os.path.expanduser('~/.config/electron/config.json'), 'r') as cfg:
            self.config = json.load(cfg)

        self.db = Connect(self.config['SQLALCHEMY_DATABASE_URI'])

    def add_user(self, username, password):
        # check and see if the user already exists
        q = self.db.session.query(self.db.base.classes.users).filter(username == username).first()

        if q:
            print('User already exists')
            return False

        new_user = self.db.base.classes.users(username=username, password=pwd_context.encrypt(password))

        self.db.session.add(new_user)
        self.db.session.commit()

        print('User added')

if __name__ == '__main__':
    uu = UserUtils()
    parser = argparse.ArgumentParser()
    parser.add_argument('--add', help='add a user')
    parser.add_argument('--password', help='the password')

    args = parser.parse_args()

    if args.add and args.password:
        uu.add_user(args.add, args.password)

