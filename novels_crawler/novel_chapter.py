from sqlalchemy.sql.schema import Column
from sqlalchemy import Integer
from sqlalchemy.sql.sqltypes import String, Text
from novels_crawler import Base

class NovelChapter(Base):
    __tablename__ = "novel_chapter"

    id = Column(Integer, primary_key=True)
    novel_id = Column(String(128))
    content = Column(Text)
    novel_chapter_index = Column(Integer)
    title = Column(String(128))