from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32))
    avatar = db.Column()
    phone = db.Column(db.Integer, unique=True)
    password = db.Column(db.Integer)
    super_user = db.Column(db.Boolean, default=False)
    sex = db.Column(db.Enum("man", "woman"),default='man')
    birth = db.Column(db.Date)
    slogan = db.Column(db.String(128))
    register_time=db.Column(db.DateTime,default=datetime.now())


class Fans(db.Model):
    __tablename__ = 'fans'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id=db.Column(db.Integer,)
    fan_id=db.Column(db.Integer,)


