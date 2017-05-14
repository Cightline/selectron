import os
import json
import datetime
from subprocess import call
from functools import wraps

from flask import Flask, request, render_template, session, redirect, url_for
from flask_login import  UserMixin, login_required, LoginManager

from sql.db_connect import Connect
from passlib.apps import custom_app_context as pwd_context


with open(os.path.expanduser('~/.config/electron/config.json'), 'r') as cfg:
        config = json.load(cfg)


app = Flask(__name__)
app.config.update(config)
app.secret_key = app.config['secret_key']

db = Connect(app.config['SQLALCHEMY_DATABASE_URI'])

values_needed = ['event','coreid','data','published_at']

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'

def alert():
    call(['echo','fuck'])

def login_user(username, password):
    
    q = db.session.query(db.base.classes.users).filter(username == username).first()

    if not q:
        return False

    if pwd_context.verify(password, q.password):
        return True

    return False



def logged_in():
    if 'logged_in' in session:
        return session['logged_in']

    return False


def login_required(f):
    @wraps(f)

    def decorated_function(*args, **kwargs):

        if logged_in():
            return f(*args, **kwargs)

        return render_template('not_authorized.html')

    return decorated_function



@app.route('/', methods=['GET', 'POST'])
@login_required
def index():

    return render_template('index.html')


@app.route('/post_data', methods=['GET', 'POST'])
def post_data():
    if request.method == 'POST':
        #print(request.values)

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


@app.route('/log', methods=['GET'])
@login_required
def log():
    q = db.session.query(db.base.classes.events).all()


    return render_template('log.html', q=q)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':

        password = request.form.get('password')
        username = request.form.get('username')

        if not username:
            return render_template('error.html', msg='no username given')

        elif not password:
            return render_template('error.html', msg='no password given')

        result = login_user(username, password)

        if not result:
            return render_template('error.html', msg='unable to log you in')

        else:
            session['logged_in'] = True
            return render_template('success.html', msg='successfully logged in')

        
@app.route('/logout', methods=['GET', 'POST'])
def logout():

    if session['logged_in'] == True:
        session['logged_in'] = False
        return render_template('success.html', msg='you have been logged out')

    
    return render_template('error.html', msg='you were not logged in')

    


if __name__ == '__main__':
    app.run(host=app.config['host'], port=app.config['port'], debug=app.config['debug'])
