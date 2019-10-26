from datetime import datetime
import logging
import logging.config
import os
from pprint import pprint

from factiva import settings
from factiva.models import Session, Articles


MAIN_DIR = settings.MAIN_DIR
RTF_DIR = settings.RTF_DIR
DICTS_FOLDER = settings.DICTS_FOLDER
TRANSCRIPTS_DIR = settings.TRANSCRIPTS_DIR
MANIFEST_FILE = os.path.join(TRANSCRIPTS_DIR, settings.MANIFEST_FILE)


def create_logger():
    log_file = 'factiva_' + str(datetime.now().strftime('%Y-%m-%d')) + '.log'
    logging.config.fileConfig('log.ini', defaults={'logfilename': log_file}, disable_existing_loggers=False)
    return logging.getLogger(__name__)


def check_strings(text):
    if text.startswith('Copyright:'):
        return True
    if 'reserves the right to make changes to documents, content, or other information on this web site without obligation to notify any person of such changes.' in text:
        return True
    return False


logger = create_logger()


if __name__ == '__main__':
    logger.info('*** Cleanup Started...')
    session = Session()
    articles = session.query(Articles.id, Articles.text).all()
    for article in articles:
        pg_list = article.text.split('\n[')
        if len(pg_list) > 0:
            new_pgs = []
            for i, pg in enumerate(pg_list):
                if check_strings(pg) is False:
                    new_pgs.append(pg)
        new_article = session.query(Articles).filter(Articles.id == article.id).one()
        new_article.text_clean = '\n['.join(new_pgs)
        session.commit()
        print(f'Updated {article.id}')
