# -*- coding: utf-8 -*-
import json

from flask import Flask, request
from flask_cors import CORS, cross_origin
from loguru import logger
from src.connect_mysql import db, DonorInfo, add, query, query_all, query_today_num
from json import dumps
from datetime import date, datetime

app = Flask(__name__)
cors = CORS(app)


class Config(object):
    """配置数据库参数"""
    # 设置连接数据库地URL
    user = 'root'
    password = '0629'
    database = 'test_db'

    app.config["JSON_AS_ASCII"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql+pymysql://{user}:{password}@127.0.0.1:3306/{database}'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    app.config['SQLALCHEMY_ECHO'] = True


class ComlexEncoder(json.JSONEncoder):
    """
    重写构造json类，遇到日期时间特殊处理，其余使用内置
    调用：dumps(data, cls=ComlexEncoder)
    """

    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, o)


# app读取设置参数
app.config.from_object(Config)
# db方法绑定app
db.init_app(app)

with app.app_context():
    db.create_all()
    logger.debug('初始化数据库')


def donor_to_json(di: DonorInfo):
    res = {
        "name": di.name,
        "age": di.age,
        "gender": di.gender,
        "id_num": di.id_num,
        "sample_type": di.sample_type,
        "sample_quantity": di.sample_quantity,
        "date": di.date,
        "place": di.place,
        "phone": di.phone,
        "serial": di.serial,
        "available": di.available,
        "create_time": di.create_time,
        "update_time": di.update_time
    }
    return dumps(res, ensure_ascii=False, cls=ComlexEncoder)


@app.route("/add", methods=['POST'])
def add_info():
    serial_num = query_today_num() + 1

    def choose_sample_code(sample: str):
        """
        根据传入的样品类型自动选择流水号的代号
        :param sample: str, 样品类型
        :return: str,
        """
        if sample == "骨髓":
            return "B"
        elif sample == "脐带":
            return "U"
        else:
            raise

    name = request.json.get('name')
    age = request.json.get('age')
    gender = request.json.get('gender')
    id_num = request.json.get('id_num')
    sample_type = request.json.get('sample_type')
    sample_quantity = request.json.get('sample_quantity')
    date = request.json.get('date')
    place = request.json.get('place')
    phone = request.json.get('phone')
    # 根据录入日期和当天第几个生成流水号
    serial = f'{choose_sample_code(sample_type)}{datetime.today().strftime("%Y%m%d")}{str(serial_num).rjust(3, "0")}'
    available = request.json.get('available')

    res = add(name, age, gender, id_num, sample_type, sample_quantity, date, place, phone, serial, available)
    # logger.debug("写入成功")
    return res


@app.route("/quest_all", methods=['POST'])
def quest_all():
    res = query_all()
    res_list = []
    for di in res:
        res_list.append({
            "name": di.name,
            "age": di.age,
            "gender": di.gender,
            "id_num": di.id_num,
            "sample_type": di.sample_type,
            "sample_quantity": di.sample_quantity,
            "date": di.date,
            "place": di.place,
            "phone": di.phone,
            "serial": di.serial,
            "available": di.available,
            "create_time": di.create_time,
            "update_time": di.update_time
        })
        logger.debug(res_list)
    return dumps(res_list, ensure_ascii=False, cls=ComlexEncoder)


@app.route("/quest_num", methods=['POST'])
def quest_num():
    return query_today_num()
