import os 
from dotenv import load_dotenv 



load_dotenv()

Base_Dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = True
    SECRET_KEY=os.environ.get('SECRET_KEY') or "somethingveryhard"
    
    @staticmethod
    def init_app(self, app):
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_URI') or \
        "sqlite:///" + os.path.join(Base_Dir, "dev-data.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    


class TestingDeveloping(Config):
    SQLALCHEMY_DATABASE_URI=os.environ.get('TEST_URI') or \
        "sqlite:///" + os.path.join(Base_Dir, "test-data.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = True




config = {
    "default": DevelopmentConfig,
    "development": DevelopmentConfig,
    "testing": TestingDeveloping
}