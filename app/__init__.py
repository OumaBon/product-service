from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate


from config import config




db = SQLAlchemy()
migrate = Migrate()
cors = CORS()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=["http://localhost:3000"])
    
    
    # from app.api_v1 import api 
    from app.api_v2 import api
    
    app.register_blueprint(api)
    
    
    return app 