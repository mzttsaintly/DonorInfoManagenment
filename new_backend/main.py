from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import date, datetime
from loguru import logger

from sqlalchemy.orm import Session
from sql_app.database import SessionLocal, engine
from sql_app import crud, models, schemas

from fastapi.middleware.cors import CORSMiddleware

from sql_app import secret_key

ALGORITHM = "HS256"
SECRET_KEY = secret_key.secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = 30

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 跨域
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Welcome"}


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


@app.post("/add")
def add_info(new_info: schemas.DonorInfoBase, db: Session = Depends(get_db)):
    # logger.info('用户名为' + str(current_user.user_name))
    # logger.info('用户权限为' + str(current_user.authority))
    serial_num = crud.query_today_num(db, new_info.date) + 1
    res = crud.add_donorInfo(db, name=new_info.name, age=new_info.age, gender=new_info.gender,
                             id_num=new_info.id_num, sample_type=new_info.sample_type,
                             sample_quantity=new_info.sample_quantity, date=new_info.date,
                             place=new_info.place, phone=new_info.phone,
                             serial=f'{datetime.today().strftime("%Y%m%d")}_{get_sample_code(new_info.sample_type)}_{str(serial_num).rjust(3, "0")}',
                             available=True)
    return res


@app.get("/query_all")
def query_all(db: Session = Depends(get_db)):
    return crud.get_donorInfo_all(db)


@app.post("/query_datas")
def query_datas(query_date: schemas.QueryDateBase, db: Session = Depends(get_db)):
    return crud.query_date(db, start=query_date.start_time, end=query_date.end_time)


@app.post("/fuzzy_query")
def fuzzy_query(keyword: schemas.FuzzyKeywordBase, db: Session = Depends(get_db)):
    return crud.fuzzy_query_donorInfo(db, attr_name=keyword.keyword, con=keyword.con)


@app.get("/today_num")
def get_today_num(today: str = str(date.today()), db: Session = Depends(get_db)):
    return crud.query_today_num(db, today)
