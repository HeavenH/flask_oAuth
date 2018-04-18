from flask import Flask, redirect, url_for
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
from os import environ, path
from flask_login import UserMixin, LoginManager, logout_user, current_user, login_required, login_user
from flask_sqlalchemy import SQLAlchemy
from flask_dance.consumer import oauth_authorized
from sqlalchemy.orm.exc import NoResultFound

app = Flask(__name__)
basedir = path.abspath(path.dirname(__file__))
app.secret_key = '04uth'
environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'h34v3n'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path.join(basedir,
'storage.db')

blueprint = make_twitter_blueprint(
    api_key = 'poqhBB46gizr0YP56urHXv919',
    api_secret = '8yk6ZqyU6gxqeb3sEKCkzQDyVupdVc21tI4y4zwdLqpr7s6NMU',
)
app.register_blueprint(blueprint, url_prefix='/authorized')

db = SQLAlchemy(app)
lm = LoginManager(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)

@app.route('/')
def index():
    if not twitter.authorized:
        return redirect(url_for('twitter.login'))
    auth = twitter.get('account/settings.json')
    auth_json = auth.json()
    return 'you are logged with twitter {}'.format(auth_json['screen_name'])

@oauth_authorized.connect_via(blueprint)
def logged_in(blueprint, token):
    auth = blueprint.session.get('account/settings.json')
    if auth.ok:
        auth_json = auth.json()
        username = auth_json['screen_name']

        query = User.query.filter_by(username=username)

        try:
            user = query.one()
        except NoResultFound:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        login_user(user)

@app.route('/dashboard')
@login_required
def panel():
    return 'you are logged in as {}'.format(current_user.username)

@app.route('/bye')
@login_required
def byebye():
    return 'good bye'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('byebye'))

if __name__ == "__main__":
    app.run(debug=True)