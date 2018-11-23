from datetime import datetime
import logging
import logging.config
import os
from pprint import pprint
import re

import settings
from db_helper import Session, Articles, Analysis
from Generic_Parser import get_data


def create_logger():
    log_file = 'factiva_text_' + str(datetime.now().strftime('%Y-%m-%d')) + '.log'
    logging.config.fileConfig('log.ini', defaults={'logfilename': log_file}, disable_existing_loggers=False)
    return logging.getLogger(__name__)


def get_articles():
    session = Session()
    articles = session.query(Articles).all()
    for article in articles:
        analysed = session.query(Analysis).filter_by(id=article.id).first()
        if analysed:
            continue
        logger.info('Analysing %s', article.id)
        text = article.text.rstrip('None')
        analyzed_dict = get_data(text)
        analyzed_dict['id'] = article.id
        analyzed_dict.pop('doc_size')
        a = Analysis(**analyzed_dict)
        session.add(a)
    session.commit()


logger = create_logger()


if __name__ == "__main__":
    logger.info('*** Analyzing STARTED...')
    get_articles()
    exit()
