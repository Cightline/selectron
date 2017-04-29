import os
import json
import datetime
from subprocess import call

from flask import Flask
from flask import request

from sql.db_connect import Connect


with open(os.path.expanduser('~/.config/electron/config.json'), 'r') as cfg:
        config = json.load(cfg)


app = Flask(__name__)
app.config.update(config)

db = Connect(app.config['SQLALCHEMY_DATABASE_URI'])

values_needed = ['event','coreid','data','published_at']


def alert():
    call(['echo','fuck'])


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print(request.values)

        # make sure everything is there
        for v in values_needed:
            if v not in request.values:
                print('missing value: %s', v)
                
                return 404

        # '2017-04-29T16:46:32.321Z'
        event        = request.values['event']
        coreid       = request.values['coreid']
        data         = request.values['data']
        published_at = datetime.datetime.strptime(request.values['published_at'], '%Y-%m-%dT%H:%M:%S.%fZ')

        new_event = db.base.classes.events(name=event, coreid=coreid, data=data, published_at=published_at)

        db.session.add(new_event)
        db.session.commit()

        if data == 'detected_movment':
            alert()

        return 'ok'


    return 'error'

if __name__ == '__main__':
    app.run(host=app.config['host'], port=app.config['port'], debug=app.config['debug'])
