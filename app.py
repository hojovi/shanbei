from flask import Flask,Blueprint
from flask_login import current_user,LoginManager

from main import main

from db import User

#flask app
app=Flask(__name__)
app.secret_key=b'\x1c\xe9\xd6P\x90\x87\x8f\x82Q\xc3$\xa6\xac\xd4A\xb7\xf6\xa8<S\xcb\xc7\xcc\xb1'

#login
login_manager=LoginManager()
login_manager.setup_app(app)
login_manager.session_protection='strong'

@login_manager.user_loader
def load_user(id):
    return User.query_one(id=id)

app.register_blueprint(main)

if __name__=='__main__':
    app.run(debug=True)
