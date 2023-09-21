from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from passlib.context import CryptContext

from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def add_donorInfo(db: Session, name, age, gender, id_num, sample_type,
                  sample_quantity, date, place, phone, serial, available):
    db_info = models.DonorInfo(name=name, age=age, gender=gender, id_num=id_num, sample_type=sample_type,
                               sample_quantity=sample_quantity, date=date, place=place,
                               phone=phone, serial=serial, available=available)
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    return db_info


def get_password_hash(password):
    return pwd_context.hash(password)


def create_user(db: Session, user_name, password, authority):
    try:
        db_user = models.User(user_name=user_name, password_hash=get_password_hash(password), authority=authority)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        return "用户名不可重复"
    except SQLAlchemyError:
        return "数据错误"
    return '创建完成'


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db: Session, user_name: str):
    user = db.query(models.User).filter(models.User.user_name == user_name).one_or_none()
    return user


def authenticate_user(db: Session, user_name, password):
    user = get_user(db, user_name=user_name)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def get_donorInfo_all(db: Session):
    return db.query(models.DonorInfo).all()


def get_donorInfo_by_keyword(db: Session, keyword: str, con: str):
    filters = {keyword: con}
    return db.query(models.DonorInfo).filter_by(**filters).scalar()


def choose_attr(attr_name: str):
    """根据传入字符串返回DonorInfo类中的属性"""
    attr_dict = {
        'name': models.DonorInfo.name,
        'age': models.DonorInfo.age,
        'gender': models.DonorInfo.gender,
        'id_num': models.DonorInfo.id_num,
        'sample_type': models.DonorInfo.sample_type,
        'sample_quantity': models.DonorInfo.sample_quantity,
        'date': models.DonorInfo.date,
        'place': models.DonorInfo.place,
        'phone': models.DonorInfo.phone,
        'serial': models.DonorInfo.serial,
        'available': models.DonorInfo.available,
        'create_time': models.DonorInfo.create_time,
        'update_time': models.DonorInfo.update_time
    }
    return attr_dict[attr_name]


def fuzzy_query_donorInfo(db: Session, attr_name: str, con: str):
    return db.query(models.DonorInfo).filter(choose_attr(attr_name).ilike(f'%{con}%')).all()


def query_date(db: Session, start: str, end: str):
    starttime = start + ' ' + '0:0:0'
    endtime = end + ' ' + '23:59:59'
    return db.query(models.DonorInfo).filter(models.DonorInfo.date >= starttime) \
        .filter(models.DonorInfo.date <= endtime).order_by(models.DonorInfo.date.desc()).all()


def query_today_num(db: Session, today: str):
    res = db.query(models.DonorInfo).filter(models.DonorInfo.date == today).all()
    num = 0
    for i in res:
        num += 1
    return num


def get_all_user(db: Session):
    return db.query(models.User).all()


def change_user_authority(db: Session, user_id: int, authority: int):
    user = db.query(models.User).filter(models.User.id == user_id).update({'authority': authority})
    db.commit()
    return user
