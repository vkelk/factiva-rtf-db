from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Date, Time, Text
from sqlalchemy import exc as sqlaException
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CreateSchema

import settings

pg_config = {
    'username': settings.DB_USER,
    'password': settings.DB_PASS,
    'host': settings.DB_HOST,
    'port': settings.DB_PORT,
    'database': settings.DB_NAME,
    'schema': settings.DB_SCHEMA
}
pg_dsn = "postgresql+psycopg2://{username}:{password}@{host}:5432/{database}".format(**pg_config)
Base = declarative_base()
db_engine = create_engine(
    pg_dsn,
    connect_args={"application_name": 'factiva:' + str(__name__)},
    pool_size=100,
    pool_recycle=600,
    max_overflow=0,
    encoding='utf-8'
    )
try:
    conn = db_engine.connect()
    conn.execute("commit")
    conn.execute("create database tweet")
    conn.close()
except sqlaException.ProgrammingError:
    pass
try:
    db_engine.execute(CreateSchema(pg_config['schema']))
except sqlaException.ProgrammingError:
    pass

db_meta = MetaData(bind=db_engine, schema=pg_config['schema'])
session_factory = sessionmaker(db_engine, autocommit=True, autoflush=True)
Session = scoped_session(session_factory)


class FileInfo(Base):
    __tablename__ = 'fileinfo'
    __table_args__ = {"schema": pg_config['schema']}

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String)
    fileloc = Column(String(512))
    status = Column(String(12))
    created = Column(DateTime, default=datetime.utcnow)


class Articles(Base):
    __tablename__ = 'articles'
    __table_args__ = {"schema": pg_config['schema']}

    id = Column(String(32), primary_key=True)
    text = Column(Text)
    AN = Column(String(64))
    HL = Column(String)
    HLP = Column(String)
    SE = Column(String)
    CLM = Column(String)
    HD = Column(Text)
    CX = Column(String)
    LP = Column(Text)
    BY = Column(String)
    WC = Column(Integer)
    PD = Column(Date)
    ET = Column(Time)
    CR = Column(String)
    SN = Column(String)
    SC = Column(String)
    NGC = Column(String)
    GC = Column(String)
    ED = Column(String)
    PG = Column(String)
    VOL = Column(String)
    LA = Column(String)
    CY = Column(String)
    TD = Column(Text)
    CT = Column(String)
    RF = Column(String)
    ART = Column(String)
    CO = Column(String)
    FDS = Column(String)
    RIC = Column(String)
    IN = Column(Text)
    NS = Column(Text)
    RE = Column(Text)
    IPC = Column(String)
    IPD = Column(String)
    DE = Column(String)
    PUB = Column(String)
    created = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(db_engine)
