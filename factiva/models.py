from datetime import datetime
import logging
import uuid

from sqlalchemy import (
    create_engine, MetaData, Column, ForeignKey, inspect,
    Integer, String, DateTime, Date, Time, Text, Float, Boolean
)
from sqlalchemy import exc as sqlaException
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CreateSchema
from sqlalchemy.dialects.postgresql import UUID, JSONB

from factiva import settings

pg_config = {
    'username': settings.DB_USER,
    'password': settings.DB_PASS,
    'host': settings.DB_HOST,
    'port': settings.DB_PORT,
    'database': settings.DB_NAME,
    'schema': settings.DB_SCHEMA
}
logger = logging.getLogger(__name__)
pg_dsn = "postgresql+psycopg2://{username}:{password}@{host}:5432/postgres".format(**pg_config)
Base = declarative_base()
db_engine = create_engine(
    pg_dsn,
    connect_args={"application_name": 'factiva:' + str(__name__)},
    pool_size=200,
    pool_recycle=600,
    max_overflow=0,
    encoding='utf-8'
    )
try:
    conn = db_engine.connect()
    conn.execute("commit")
    conn.execute("create database {}".format(pg_config['database']))
    conn.close()
except sqlaException.ProgrammingError as Exception:
    pass

pg_dsn = "postgresql+psycopg2://{username}:{password}@{host}:5432/{database}".format(**pg_config)
db_engine = create_engine(
    pg_dsn,
    connect_args={"application_name": 'factiva:' + str(__name__)},
    pool_size=200,
    pool_recycle=600,
    max_overflow=0,
    encoding='utf-8'
    )
try:
    db_engine.execute(CreateSchema(pg_config['schema']))
except sqlaException.ProgrammingError:
    pass
db_meta = MetaData(bind=db_engine, schema=pg_config['schema'])
session_factory = sessionmaker(db_engine)
Session = scoped_session(session_factory)


class Articles(Base):
    __tablename__ = 'articles'
    __table_args__ = {"schema": pg_config['schema']}

    id = Column(String, primary_key=True)
    text = Column(Text)
    text_clean = Column(Text)
    CLM = Column(String)
    SE = Column(String)
    HD = Column(Text)
    BY = Column(String)
    CR = Column(String)
    WC = Column(Integer)
    PD = Column(Date)
    ET = Column(Time)
    SN = Column(String)
    SC = Column(String)
    ED = Column(String)
    PG = Column(String)
    VOL = Column(String)
    LA = Column(String)
    CY = Column(String)
    LP = Column(Text)
    TD = Column(Text)
    CT = Column(String)
    RF = Column(String)
    CO = Column(String)
    IN = Column(Text)
    NS = Column(Text)
    RE = Column(Text)
    IPC = Column(String)
    IPD = Column(String)
    PUB = Column(String)
    AN = Column(String)
    created = Column(DateTime, default=datetime.utcnow)


class Analysis(Base):
    __tablename__ = 'analysis'
    __table_args__ = {"schema": pg_config['schema']}

    id = Column(String, primary_key=True)
    word_count = Column(Integer)
    positive = Column(Float)
    negative = Column(Float)
    uncertainty = Column(Float)
    litigious = Column(Float)
    modal_weak = Column(Float)
    modal_moderate = Column(Float)
    modal_strong = Column(Float)
    constraining = Column(Float)
    alphabetic = Column(Integer)
    digits = Column(Integer)
    numbers = Column(Integer)
    avg_syllables_per_word = Column(Float)
    avg_word_length = Column(Float)
    vocabulary = Column(Integer)
    created = Column(DateTime, default=datetime.utcnow)

    def _asdict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class Company(Base):
    __tablename__ = 'companies'
    __table_args__ = {"schema": pg_config['schema']}

    gvkey = Column(String, primary_key=True)
    name = Column(String)
    factiva_name = Column(String)
    factiva_code = Column(String)


class CompanyArticle(Base):
    __tablename__ = 'company_articles'
    __table_args__ = {"schema": pg_config['schema']}

    id = Column(Integer, primary_key=True, autoincrement=True)
    gvkey = Column(String, ForeignKey(pg_config['schema'] + '.companies.gvkey'), index=True)
    article_id = Column(String, ForeignKey(pg_config['schema'] + '.articles.id'), index=True)
    main_category = Column(String)
    sub_category = Column(String)


class TradingDay(Base):
    __tablename__ = 'trading_days'
    __table_args__ = {"schema": 'public'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, index=True)
    is_trading = Column(Boolean, default=True)


class SentimentHarvard(Base):
    __tablename__ = 'sentiment_harvard'
    __table_args__ = {"schema": pg_config['schema']}

    article_id = Column(String, ForeignKey(pg_config['schema'] + '.articles.id'), primary_key=True)
    word_count = Column(Integer)
    positiv = Column(Float)
    negativ = Column(Float)
    pstv = Column(Float)
    affil = Column(Float)
    ngtv = Column(Float)
    hostile = Column(Float)
    strong = Column(Float)
    power = Column(Float)
    weak = Column(Float)
    submit = Column(Float)
    active = Column(Float)
    passive = Column(Float)
    created = Column(DateTime, default=datetime.utcnow)


class FileInfo(Base):
    __tablename__ = 'file_info'
    __table_args__ = {"schema": pg_config['schema']}

    id = Column(Integer, primary_key=True, autoincrement=True)
    gvkey = Column(String, index=True)
    fiscal_qtr = Column(String)
    document_id = Column(String, index=True)
    file_new_name = Column(String, index=True)
    co_name = Column(String)
    ticker = Column(String)
    f_name = Column(String)
    f_code = Column(String)
    article_id = Column(String, ForeignKey(pg_config['schema'] + '.articles.id'), nullable=True, default=None)


class Transcript(Base):
    __tablename__ = 'transcripts'
    __table_args__ = {"schema": pg_config['schema']}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    article_id = Column(String, ForeignKey(pg_config['schema'] + '.articles.id'), primary_key=True)
    sequence = Column(Integer)
    text = Column(String)
    author = Column(String)
    author_data = Column(JSONB)



Base.metadata.create_all(db_engine)
