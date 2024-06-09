from .account import Account
from .university import University
from .article import Article
from .following import Following
from database.conn import DBObject

tables = [University, Account, Article, Following]
DBObject()
for table in tables:
    table.__table__.create(bind=DBObject.instance.engine, checkfirst=True)
