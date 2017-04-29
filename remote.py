import datetime
import json
import os

import requests
import schedule
import dateutil.parser
from dateutil.tz import gettz




class Config():
    def __init__(self):
        self.path = os.path.expanduser('~/.config/electron/config.json')

        with open(self.path, 'r') as cfg:
            self.cfg = json.load(cfg)


    def get_config(self):
        return self.cfg



class Function():
    def __init__(self):
        self.cfg = Config().get_config()

        self.electron_id  = self.cfg['electron_id']
        self.access_token = self.cfg['access_token']

    def call_function(self, function_name, arg):
        #POST /v1/devices/:deviceId/:functionName

        var_page = requests.post('https://api.particle.io/v1/devices/%s/%s' % (self.electron_id, function_name), {'access_token':self.access_token, "arg":arg})

        if 'return_value' in var_page.json():
            print(var_page.json()['return_value'])
     
    
        else:
            print('no result')





# battery state of charge
#call_function(e_id, 'c', 'state')
# gps location
#call_function(e_id, 'c', 'location')
#call_function(e_id, 'c', 'recalibrate')

if __name__ == '__main__':
    import argparse

    f = Function()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--function', help='call a remote function')
    parser.add_argument('--option',   help='the option to send')
    args = parser.parse_args()

    
    if args.function:
        f.call_function(args.function, args.option)
    
 
