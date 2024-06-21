from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_moment import Moment
from flask_ckeditor import CKEditor


db = SQLAlchemy()
login_manager = LoginManager()
moment = Moment()
ckeditor = CKEditor()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.DevelopmentConfig')
    
    # Initializations 
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    ckeditor.init_app(app)
    
    login_manager.login_view = "auth.login"
    
    from .auth import auth
    from .views import views
    from .errors import errors
    
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(errors, url_prefix='/error')
    
    from .models import User, Post
    
    with app.app_context():
        db.create_all()
        
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    return app
 