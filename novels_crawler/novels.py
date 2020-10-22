from sqlalchemy.sql.schema import Column
from sqlalchemy import Integer
from sqlalchemy.sql.sqltypes import String
from novels_crawler import Base

class Novel(Base):
    __tablename__ = "novel"

    id = Column(Integer, primary_key=True)
    title = Column(String(128))
    author = Column(String(128))
    novel_id = Column(String(128))
    complete = Column(Integer)