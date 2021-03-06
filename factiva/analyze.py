from datetime import datetime
import logging
import os
import re

from sqlalchemy import or_

from factiva import settings
from .models import Session, Articles, Analysis, SentimentHarvard
from .Generic_Parser import get_data
from .Load_MasterDictionary import load_masterdictionary


logger = logging.getLogger(__name__)
hiv_dictionary_path = os.path.join(settings.DICTS_FOLDER, settings.HIV4_DICTIONARY_FILE)
hiv4_dictionary = load_masterdictionary(hiv_dictionary_path, True)

def analyze_artices():
    logger.info('*** Analyzing Started...')
    session = Session()
    articles = session.query(Articles.id, Articles.text) \
        .outerjoin(Analysis, Analysis.id == Articles.id)\
        .outerjoin(SentimentHarvard, SentimentHarvard.article_id == Articles.id)\
        .filter(or_(Analysis.id.is_(None), SentimentHarvard.article_id.is_(None))).all()
    i = 0
    for article in articles:
        text = article.text.rstrip('None')
        # Loughran-McDonald
        analysed = session.query(Analysis).filter_by(id=article.id).first()
        if analysed is None:
            logger.info('Analysing Loughran-McDonald for article id %s', article.id)
            lm_dict = get_data(text)
            lm_dict['id'] = article.id
            lm_dict.pop('doc_size')
            a = Analysis(**lm_dict)
            session.add(a)
        # Harvard IV-4
        sentiment_harvard = session.query(SentimentHarvard).filter_by(article_id=article.id).first()
        if sentiment_harvard is None:
            logger.info('Analysing Harvard Inquirer Categories for article id %s', article.id)
            hiv4_dict = analyze_harvard_iv4(text)
            hiv4_dict['article_id'] = article.id
            h = SentimentHarvard(**hiv4_dict)
            session.add(h)
    session.commit()
    logger.info('*** Analyzing Finished...')


def analyze_harvard_iv4(text):
    
    COLUMNS = [
        'article_id', 'word_count', 'positiv', 'negativ', 'pstv', 'affil', 'ngtv',
        'hostile', 'strong', 'power', 'weak', 'submit', 'active', 'passive'
        ]
    
    vdictionary = {}
    _odata = [0] * 15
    total_syllables = 0
    word_length = 0
    tokens = re.findall('\w+', text)
    for token in tokens:
        token = token.upper()
        if not token.isdigit() and len(token) > 1 and token in hiv4_dictionary:
            
            _odata[1] += 1  # word count
            word_length += len(token)
            if token not in vdictionary:
                vdictionary[token] = 1
            if hiv4_dictionary[token].positiv: _odata[2] += 1
            if hiv4_dictionary[token].negativ: _odata[3] += 1
            if hiv4_dictionary[token].pstv: _odata[4] += 1
            if hiv4_dictionary[token].affil: _odata[5] += 1
            if hiv4_dictionary[token].ngtv: _odata[6] += 1
            if hiv4_dictionary[token].hostile: _odata[7] += 1
            if hiv4_dictionary[token].strong: _odata[8] += 1
            if hiv4_dictionary[token].power: _odata[9] += 1
            if hiv4_dictionary[token].weak: _odata[10] += 1
            if hiv4_dictionary[token].submit: _odata[11] += 1
            if hiv4_dictionary[token].active: _odata[12] += 1
            if hiv4_dictionary[token].passive: _odata[13] += 1
    
    # Convert counts to %
    try:
        for i in range(2, 13 + 1):
            _odata[i] = (_odata[i] / _odata[1]) * 100
    except ZeroDivisionError:
        pass
    
    return dict(zip(COLUMNS, _odata))