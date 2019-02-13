from datetime import datetime
import logging


from factiva import settings
from .models import Session, Articles, Analysis
from .Generic_Parser import get_data


logger = logging.getLogger(__name__)


def analyze_artices():
    session = Session()
    articles = session.query(Articles) \
        .outerjoin(Analysis, Analysis.id == Articles.id)\
        .filter(Analysis.id.is_(None)).all()
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
