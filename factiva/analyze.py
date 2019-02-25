from datetime import datetime
import logging
import os
import re

from factiva import settings
from .models import Session, Articles, Analysis
from .Generic_Parser import get_data
from .Load_MasterDictionary import load_masterdictionary


logger = logging.getLogger(__name__)
hiv_dictionary_path = os.path.join(settings.DICTS_FOLDER, settings.HIV4_DICTIONARY_FILE)
hiv4_dictionary = load_masterdictionary(hiv_dictionary_path, True)

def analyze_artices():
    logger.info('*** Analyzing Started...')
    session = Session()
    # articles = session.query(Articles) \
    #     .outerjoin(Analysis, Analysis.id == Articles.id)\
    #     .filter(Analysis.id.is_(None)).all()
    articles = session.query(Articles).all()
    i = 0
    for article in articles:
        text = article.text.rstrip('None')
        # Loughran-McDonald
        analysed = session.query(Analysis).filter_by(id=article.id).first()
        if analysed is None:
            logger.info('Analysing %s', article.id)
            lm_dict = get_data(text)
            lm_dict['id'] = article.id
            lm_dict.pop('doc_size')
            a = Analysis(**lm_dict)
            session.add(a)
        else:
            print('LM DATA')
            print(analysed._asdict())
        # Harvard IV-4
        hiv4_dict = analyze_harvard_iv4(text)
        hiv4_dict['id'] = article.id
        print('Harvard DATA')
        print(hiv4_dict)
        i += 1
        if i > 5:
            exit()
    session.commit()
    logger.info('*** Analyzing Finished...')


def analyze_harvard_iv4(text):
    
    COLUMNS = [
        'id', 'word_count', 'Positiv', 'Negativ', 'Pstv', 'Affil', 'Ngtv',
        'Hostile', 'Strong', 'Power', 'Weak', 'Submit', 'Active', 'Passive'
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
            if hiv4_dictionary[token].Positiv: _odata[2] += 1
            if hiv4_dictionary[token].Negativ: _odata[3] += 1
            if hiv4_dictionary[token].Pstv: _odata[4] += 1
            if hiv4_dictionary[token].Affil: _odata[5] += 1
            if hiv4_dictionary[token].Ngtv: _odata[6] += 1
            if hiv4_dictionary[token].Hostile: _odata[7] += 1
            if hiv4_dictionary[token].Strong: _odata[8] += 1
            if hiv4_dictionary[token].Power: _odata[9] += 1
            if hiv4_dictionary[token].Weak: _odata[10] += 1
            if hiv4_dictionary[token].Submit: _odata[11] += 1
            if hiv4_dictionary[token].Active: _odata[12] += 1
            if hiv4_dictionary[token].Passive: _odata[13] += 1
    
    # Convert counts to %
    for i in range(2, 13 + 1):
        _odata[i] = (_odata[i] / _odata[1]) * 100
    
    return dict(zip(COLUMNS, _odata))