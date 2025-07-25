import os 
from flask_migrate import Migrate 
from app import create_app, db 




app = create_app(os.getenv('FLASK_ENV', 'default'))
migrate=Migrate(app, db)




@app.shell_context_processor
def make_shell_context():
    return {"db": db}