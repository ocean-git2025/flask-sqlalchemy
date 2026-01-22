from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('app.config.Config')

db = SQLAlchemy(app)

from app.routes.user import user_bp
app.register_blueprint(user_bp)
