from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Initialisation vide des extensions (elles seront liées à l'app plus tard)
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()