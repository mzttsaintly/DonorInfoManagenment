import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint, DateTime

from .database import Base


class DonorInfo(Base):
    """
        数据模板
    """
    __tablename__ = "DonorInfo"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    age = Column(String)
    gender = Column(String)
    id_num = Column(String)
    sample_type = Column(String)
    sample_quantity = Column(String)
    date = Column(String)
    place = Column(String)
    phone = Column(String)
    serial = Column(String)
    available = Column(Boolean)
    create_time = Column(DateTime, default=datetime.datetime.now)
    update_time = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class User(Base):
    """
    创建用户信息模板
    """
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String, unique=True)
    password_hash = Column(String)
    # 1为上传报告的权限，2为修改物料设备信息的权限，4为增加新用户的权限，可累加
    authority = Column(Integer)
