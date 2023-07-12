from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

# 创建对象，所有数据库方法从db取
db = SQLAlchemy()


class DonorInfo(db.Model):
    # 创建数据表模板
    __tablename__ = 'DonorInfo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)  # 名字
    age = db.Column(db.String)  # 年龄
    gender = db.Column(db.String)  # 性别
    id_num = db.Column(db.String)  # 身份证号码
    sample_type = db.Column(db.String)  # 采样类型
    sample_quantity = db.Column(db.String)  # 采样数量
    date = db.Column(db.String)  # 采样时间
    place = db.Column(db.String)  # 采样地点
    phone = db.Column(db.String)  # 联系电话
    serial = db.Column(db.Integer)  # 流水号
    available = db.Column(db.Boolean)  # 是否为可用数据

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

    except SQLAlchemyError:
        return
    return "写入完成"
