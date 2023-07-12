# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from loguru import logger
from src.connect_mysql import db, DonorInfo, add, query, query_all

app = Flask(__name__)
cors = CORS(app)


class Config(object):
    """配置数据库参数"""
    # 设置连接数据库地URL
    user = 'root'
    password = 'wy19970629'
    database = 'test_db'

    app.config["JSON_AS_ASCII"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql+pymysql://{user}:{password}@127.0.0.1:3306/{database}'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    app.config['SQLALCHEMY_ECHO'] = True


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
    }
    return jsonify(res)


@app.route("/add", methods=['POST'])
def add_info():
    name = request.json.get('name')
    age = request.json.get('age')
    gender = request.json.get('gender')
    id_num = request.json.get('id_num')
    sample_type = request.json.get('sample_type')
    sample_quantity = request.json.get('sample_quantity')
    date = request.json.get('date')
    place = request.json.get('place')
    phone = request.json.get('phone')
    serial = request.json.get('serial')
    available = request.json.get('available')

    res = add(name, age, gender, id_num, sample_type, sample_quantity, date, place, phone, serial, available)
    logger.debug("写入成功")
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
        })
        logger.debug(res_list)
    return jsonify(res_list)
