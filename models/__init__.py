from .account import Account
from .university import University
from database.conn import DBObject

tables = [University, Account]
DBObject()
for table in tables:
    table.__table__.create(bind=DBObject.instance.engine, checkfirst=True)
