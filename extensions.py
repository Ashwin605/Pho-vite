from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_compress import Compress
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()
compress = Compress()
mail = Mail()
