import concurrent.futures as cf
from datetime import datetime
import logging
import logging.config
import os
from pprint import pprint
import re

import settings
from db_helper import Session, Articles, Analysis, Company, CompanyArticle, sessionmaker, db_engine


def create_logger():
    log_file = 'factiva_text_' + str(datetime.now().strftime('%Y-%m-%d')) + '.log'
    logging.config.fileConfig('log.ini', defaults={'logfilename': log_file}, disable_existing_loggers=False)
    return logging.getLogger(__name__)


def get_unmatched_articles():
    # session = Session()
    try:
        Session = sessionmaker(bind=db_engine, autoflush=False)
        session = Session()
        q = session.query(Articles) \
            .outerjoin(CompanyArticle, CompanyArticle.article_id == Articles.id)\
            .filter(CompanyArticle.article_id.is_(None))
        return (r for r in q.execution_options(stream_results=True))
    except Exception:
        logger.exception('message')
        raise


def get_company_by_code(code):
    try:
        session = Session()
        q = session.query(Company).filter(Company.factiva_code == code).first()
        if q is None:
            logger.warning('Could not match company with code %s', code)
            return None
        return q
    except Exception:
        logger.exception('message')
        raise


def insert_comp_art(organization, article):
    try:
        session = Session()
        org_list = organization.split(':')
        code = org_list[0].strip().upper()
        company = get_company_by_code(code)
        if company is None:
            return None
        com_art = CompanyArticle(
            gvkey=company.gvkey,
            article_id=article.id
        )
        if article.NS is not None:
            ns_list = article.NS.split('|')
        else:
            ns_list = []
        i = 0
        for cat in ns_list:
            cat_list = cat.split(':')
            match_cnum = re.match('c\d+', cat_list[0].strip())
            if i > 2 or match_cnum is None:
                continue
            i += 1
            if i == 1:
                com_art.main_category = cat_list[1].strip()
            if i == 2:
                com_art.sub_category = cat_list[1].strip()
        session.add(com_art)
        session.commit()
        logger.info('Matched company %s to article %s', company.factiva_name, com_art.article_id)
        session.close()
    except Exception:
        logger.exception('message')
        raise


def main_worker(article):
    co_list = article.CO.split('|')
    if len(co_list) > 0:
        for organization in co_list:
            inserted = insert_comp_art(organization, article)
    else:
        logger.warning('Could not get company codes for article %s', article.id)
    Session.remove()


def match_articles():
    with cf.ThreadPoolExecutor(max_workers=16) as executor:
        try:
            executor.map(main_worker, get_unmatched_articles())
        except BaseException as e:
            logger.error(str(e))
            raise
    # single thread
    # for article in get_unmatched_articles(session):
    #     co_list = article.CO.split('|')
    #     if len(co_list) > 0:
    #         session = Session()
    #         for organization in co_list:
    #             inserted = insert_comp_art(organization, article, session)
    #     else:
    #         logger.warning('Could not get company codes for article %s', article.id)
    #         continue


logger = create_logger()


if __name__ == "__main__":
    logger.info('*** Matching STARTED...')
    match_articles()
    logger.info('*** Matching COMPLETED...')
