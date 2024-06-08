from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.DevelopmentConfig')
    # Initializations 
    db.init_app(app)
    
    from .auth import auth
    from .views import views
    
    app.register_blueprint(auth, url_prefix='/auth')    
    app.register_blueprint(views, url_prefix='/')
    
    from .models import User
    
    with app.app_context():
        db.create_all()
    
    return app
 