import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

# 创建对象，所有数据库方法从db取
db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.String(128))  # 名字
    password = db.Column(db.String(128))  # 密码
