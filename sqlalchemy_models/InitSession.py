#1/usr/bin/python
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

def get_engine():
    engine = create_engine("mysql://zabbix:zabbix@SCM@10.183.97.42/zabbix?charset=utf8")
    return engine

def get_session(autocommit=True, expire_on_commit=False):
    Session = sessionmaker(bind=get_engine(),autocommit = autocommit, expire_on_commit = expire_on_commit)
    session = Session()
    return session
