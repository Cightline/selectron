import os
import json


from sqlalchemy.ext.automap     import automap_base
from sqlalchemy                 import create_engine
from sqlalchemy_utils.functions import database_exists, drop_database
from sql import initialize_sql

from sql.events import Event


class CreateDB():
    def __init__(self):

        with open(os.path.expanduser('~/.config/electron/config.json'), 'r') as cfg:
            self.config = json.load(cfg)

        self.db_path = self.config['SQLALCHEMY_DATABASE_URI']
        self.base    = automap_base()
       
    def create(self, confirm=False):

        if confirm:
            if database_exists(self.db_path):
                i = input('this will recreate the database, continue? [y/n]: ').lower().strip() 

                if i != 'y' and i != 'yes':
                    exit()
            
                drop_database(self.db_path)

        
        initialize_sql(create_engine(self.db_path, echo=False))



if __name__ == '__main__':

    cdb = CreateDB()
    r   = cdb.create(True)

    if r == None:
        print('databse created')
        
    else:
        print('unable to create the database')
        exit()
