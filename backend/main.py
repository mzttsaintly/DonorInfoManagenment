# -*- coding: utf-8 -*-
import getpass
import json
from datetime import date, datetime
from json import dumps

from flask import Flask, request
from flask_cors import CORS
from loguru import logger

from src.connect_mysql import db, DonorInfo, add, query, query_all, query_today_num, query_paginate, query_date, \
    fuzzy_query

user = input("请输入用户名：")
# password = input("请输入密码：")
password = getpass.getpass("请输入密码：")

app = Flask(__name__)
cors = CORS(app)


class Config(object):
    """配置数据库参数"""
    # 设置连接数据库地URL
    # user = 'root'
    # password = '0629'
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
    """
    单个信息转换为json
    """
    res = {
        "name": di.name,
        "age": di.age,
        "gender": di.gender,
        "id_num": di.id_num,
        "sample_type": di.sample_type,
        "sample_quantity": di.sample_quantity,
        "date": di.date.strftime("%Y-%m-%d"),
        "place": di.place,
        "phone": di.phone,
        "serial": di.serial,
        "available": di.available,
        "create_time": di.create_time,
        "update_time": di.update_time
    }
    return dumps(res, ensure_ascii=False, cls=ComlexEncoder)


def donors_to_json(dis):
    res_list = []
    for di in dis:
        res_list.append({
            "name": di.name,
            "age": di.age,
            "gender": di.gender,
            "id_num": di.id_num,
            "sample_type": di.sample_type,
            "sample_quantity": di.sample_quantity,
            "date": di.date.strftime("%Y-%m-%d"),
            "place": di.place,
            "phone": di.phone,
            "serial": di.serial,
            "available": di.available,
            "create_time": di.create_time,
            "update_time": di.update_time
        })
        logger.debug(res_list)
    return dumps(res_list, ensure_ascii=False, cls=ComlexEncoder)


def get_sample_code(sample_type: str):
    """
    根据传入的样品类型返回对应样品代码
    """
    sample_code = {
        "骨髓": "BM",
        "外周血": "PB",
        "脐带血": "CB",
        "脐带": "UC",
        "其他组织样品": "X"
    }
    return sample_code[sample_type]


@app.route("/add", methods=['POST'])
def add_info():
    """
    添加信息进入数据库
    """
    serial_num = query_today_num() + 1

    name = request.json.get('name')
    age = request.json.get('age')
    gender = request.json.get('gender')
    id_num = request.json.get('id_num')
    sample_type = request.json.get('sample_type')
    sample_quantity = request.json.get('sample_quantity')
    date = request.json.get('date')
    place = request.json.get('place')
    phone = request.json.get('phone')
    # 根据录入日期和当天第几个数据生成流水号
    serial = f'{datetime.today().strftime("%Y%m%d")}_{get_sample_code(sample_type)}_{str(serial_num).rjust(3, "0")}'
    available = True

    res = add(name, age, gender, id_num, sample_type, sample_quantity, date, place, phone, serial, available)

    res_info = {
        "name": name,
        "age": age,
        "gender": gender,
        "id_num": id_num,
        "sample_type": sample_type,
        "sample_quantity": sample_quantity,
        "date": date,
        "place": place,
        "phone": phone,
        "serial": serial,
        "res": res
    }
    # logger.debug("写入成功")
    return res_info


@app.route("/quest_all", methods=['POST'])
def quest_all():
    """
    获取全部条目
    """
    res = query_all()
    return donors_to_json(res)


# @app.route("/quest_num", methods=['POST'])
# def quest_num():
#     return query_today_num()


@app.route("/paginate_query", methods=['POST'])
def paginate_query():
    page = request.json.get('currentPage')
    pn = query_paginate(page=page)
    pages = pn.page
    total_pages = pn.pages
    res = donors_to_json(pn.items)
    res_list = {
        "currentPage": pages,
        "total": total_pages,
        "res": res
    }
    # return res
    return dumps(res_list, ensure_ascii=False, cls=ComlexEncoder)


@app.route("/query_by_param", methods=['POST'])
def query_by_param():
    keyword = request.json.get('keyword')
    con = request.json.get('con')
    res = query(keyword, con)
    return donors_to_json(res)


@app.route("/query_datas", methods=['POST'])
def query_datas():
    """
    根据起始时间和结束时间搜索
    """
    start_time = request.json.get('start_time')
    end_time = request.json.get('end_time')
    res = query_date(start_time, end_time)
    return donors_to_json(res)


@app.route("/fuzzy_query", methods=['POST'])
def fuzzy_query_from():
    """
    模糊查询
    """
    attr_name = request.json.get('attr_name')
    con = request.json.get('con')
    res = fuzzy_query(attr_name, con)
    return donors_to_json(res)
