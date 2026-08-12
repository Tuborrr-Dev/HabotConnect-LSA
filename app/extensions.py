"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager

jwt = JWTManager()
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
