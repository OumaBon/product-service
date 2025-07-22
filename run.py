#!/usr/bin/env python3
import os



from app import create_app, db 


port = int(os.getenv("PORT", 5000))


app = create_app(os.getenv('FLASK_ENV', "default"))



with app.app_context():
    db.create_all()
    app.run(port=port)