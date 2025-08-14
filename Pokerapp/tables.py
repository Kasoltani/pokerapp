import datetime as dt
from flask_login import UserMixin
from . import db



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(255), nullable=False)
    date_joined = db.Column(
        db.DateTime(timezone=True),  # tell SQLAlchemy this is tz-aware
        nullable=False,
        default=lambda: dt.datetime.now(dt.timezone.utc)
    )