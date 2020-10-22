from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import base
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://root:w1234@81.68.242.216/common_server')
Base = declarative_base()

DBSession = sessionmaker(bind=engine)
session = DBSession()