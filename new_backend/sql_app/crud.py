from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from passlib.context import CryptContext

from . import models, schemas


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def add_donorInfo(db: Session, name, age, gender, id_num, sample_type,
                  sample_quantity, date, place, phone, serial, available):
    db_info = models.DonorInfo(name=name, age=age, id_num=id_num, sample_type=sample_type,
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
