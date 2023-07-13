import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

# 创建对象，所有数据库方法从db取
db = SQLAlchemy()


class DonorInfo(db.Model):
    # 创建数据表模板
    __tablename__ = 'DonorInfo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))  # 名字
    age = db.Column(db.Integer)  # 年龄
    gender = db.Column(db.String(128))  # 性别
    id_num = db.Column(db.String(128))  # 身份证号码
    sample_type = db.Column(db.String(128))  # 采样类型
    sample_quantity = db.Column(db.String(128))  # 采样数量
    date = db.Column(db.DateTime)  # 采样时间
    place = db.Column(db.String(128))  # 采样地点
    phone = db.Column(db.String(128))  # 联系电话
    serial = db.Column(db.String(128))  # 每日流水号
    available = db.Column(db.Boolean)  # 是否为可用数据
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)  # 创建时间
    update_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return f'Donor(name{self.name}, ' \
               f'age{self.age}, ' \
               f'gender{self.gender}, ' \
               f'id_num{self.id_num}, ' \
               f'sample_type{self.sample_type}, ' \
               f'sample_quantity{self.sample_quantity}, ' \
               f'date,{self.date}' \
               f' place{self.place}, ' \
               f'phone{self.phone}, ' \
               f'serial{self.serial}, ' \
               f'available{self.available})'


def add(name, age, gender, id_num, sample_type, sample_quantity, date, place, phone, serial, available):
    """
    给数据库加入数据
    :param name: 名字
    :param age: 年龄
    :param gender: 性别
    :param id_num: 身份证号码
    :param sample_type: 采样类型
    :param sample_quantity: 采样数量
    :param date: 采样时间
    :param place: 采样地点
    :param phone: 联系电话
    :param serial: 流水号
    :param available: 是否为可用数据
    :return: str,提示写入是否完成
    """
    try:
        db.session.add(DonorInfo(
            name=name,
            age=age,
            gender=gender,
            id_num=id_num,
            sample_type=sample_type,
            sample_quantity=sample_quantity,
            date=date,
            place=place,
            phone=phone,
            serial=serial,
            available=available
        ))
        db.session.commit()
    except:
        raise
    # except SQLAlchemyError:
    #     return "写入失败"
    return "写入完成"


def query(keyword: str, con: str):
    """
    动态地查询数据库信息
    :param keyword: 需查询地项目
    :param con: 查询地条件(精确)
    :return: 符合条件地数据库对象
    """
    filters = {keyword: con}
    res = db.session.execute(db.select(DonorInfo).filter_by(**filters)).scalars()
    return res


def query_all():
    """
    返回所有对象
    :return: 一个包含了所有对象的列表
    """
    res = db.session.execute(db.select(DonorInfo).order_by(DonorInfo.serial)).scalars()
    return res


def query_paginate():
    res = db.session.paginate(db.select(DonorInfo).order_by(DonorInfo.serial))


def query_today_num():
    """
    获取今日的数据条目数量
    """
    time_now = datetime.datetime.today()
    # 筛选出当天的录入信息
    res = db.session.execute(db.select(DonorInfo).filter(db.cast(DonorInfo.create_time, db.DATE) ==
                                                         db.cast(datetime.datetime.now(), db.DATE))).scalars()
    # 没有len方法，手动获取录入信息的数量
    num = 0
    for i in res:
        num += 1
    return num
