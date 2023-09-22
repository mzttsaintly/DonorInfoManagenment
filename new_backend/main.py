from fastapi import Depends, FastAPI, HTTPException, Form, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import date, datetime, timedelta
from loguru import logger
from jose import JWTError, jwt
from typing import Union

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


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user(db, user_name=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/login", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


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
async def add_info(new_info: schemas.DonorInfoBase, db: Session = Depends(get_db),
                   current_user: schemas.UserBase = Depends(get_current_user)):
    logger.info('用户名为' + str(current_user.user_name))
    logger.info('用户权限为' + str(current_user.authority))
    if current_user.authority >= 2:
        serial_num = crud.query_today_num(db, new_info.date) + 1
        res = crud.add_donorInfo(db, name=new_info.name, age=new_info.age, gender=new_info.gender,
                                 id_num=new_info.id_num, sample_type=new_info.sample_type,
                                 sample_quantity=new_info.sample_quantity, date=new_info.date,
                                 place=new_info.place, phone=new_info.phone,
                                 serial=f'{datetime.today().strftime("%Y%m%d")}_{get_sample_code(new_info.sample_type)}_{str(serial_num).rjust(3, "0")}',
                                 available=True)
        return res
    else:
        return "权限不足"


@app.get("/query_all")
async def query_all(db: Session = Depends(get_db), current_user: schemas.UserBase = Depends(get_current_user)):
    if current_user.authority >= 1:
        return crud.get_donorInfo_all(db)
    else:
        return "权限不足"


@app.post("/query_datas")
async def query_datas(query_date: schemas.QueryDateBase, db: Session = Depends(get_db),
                      current_user: schemas.UserBase = Depends(get_current_user)):
    if current_user.authority >= 1:
        return crud.query_date(db, start=query_date.start_time, end=query_date.end_time)
    else:
        return "权限不足"


@app.post("/fuzzy_query")
async def fuzzy_query(keyword: schemas.FuzzyKeywordBase, db: Session = Depends(get_db),
                      current_user: schemas.UserBase = Depends(get_current_user)):
    if current_user.authority >= 1:
        return crud.fuzzy_query_donorInfo(db, attr_name=keyword.keyword, con=keyword.con)
    else:
        return "权限不足"


@app.get("/today_num")
async def get_today_num(today: str = str(date.today()), db: Session = Depends(get_db)):
    return crud.query_today_num(db, today)


@app.post("/user/create_user")
async def create_user(username: str = Form(), password: str = Form(), authority: int = Form(),
                      db: Session = Depends(get_db),
                      current_user: schemas.UserBase = Depends(get_current_user)):
    logger.info('用户名为' + str(current_user.user_name))
    logger.info('用户权限为' + str(current_user.authority))
    if current_user.authority >= 4:
        res = crud.create_user(db, user_name=username, password=password, authority=authority)
        return res
    else:
        return "权限不足"


# @app.post("/user/root_user")
# async def create_user(username: str = Form(), password: str = Form(), authority: int = Form(),
#                       db: Session = Depends(get_db)):
#     return crud.create_user(db, user_name=username, password=password, authority=authority)


@app.get("/user/me/", response_model=schemas.UserBase)
async def read_user_me(current_user: schemas.UserBase = Depends(get_current_user)):
    return current_user


@app.get("/user/get_all")
async def get_all_user(db: Session = Depends(get_db),
                       current_user: schemas.UserBase = Depends(get_current_user)):
    logger.info('用户名为' + str(current_user.user_name))
    logger.info('用户权限为' + str(current_user.authority))
    if current_user.authority >= 4:
        res = crud.get_all_user(db)
        res_list = []
        for i in res:
            res_list.append({"id": i.id, "user_name": i.user_name, "authority": i.authority})
        return res_list
    else:
        return "权限不足"


@app.post("/user/change_authority")
async def change_authority(user: schemas.UserBase, db: Session = Depends(get_db),
                           current_user: schemas.UserBase = Depends(get_current_user)):
    logger.info('用户名为' + str(current_user.user_name))
    logger.info('用户权限为' + str(current_user.authority))
    if current_user.authority >= 4:
        return crud.change_user_authority(db, user_id=user.id, authority=user.authority)
    else:
        return "权限不足"
