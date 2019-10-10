import argparse
from datetime import datetime
import logging
import logging.config
import os

import pandas as pd

from factiva import settings
from factiva.importer import process_file
from factiva.analyze import analyze_artices
from factiva.counts import get_articles, get_analysis, slugify, validate_date


MAIN_DIR = settings.MAIN_DIR
RTF_DIR = settings.RTF_DIR
DICTS_FOLDER = settings.DICTS_FOLDER
TRANSCRIPTS_DIR = settings.TRANSCRIPTS_DIR
MANIFEST_FILE = os.path.join(TRANSCRIPTS_DIR, settings.MANIFEST_FILE)


def create_logger():
    log_file = 'factiva_' + str(datetime.now().strftime('%Y-%m-%d')) + '.log'
    logging.config.fileConfig('log.ini', defaults={'logfilename': log_file}, disable_existing_loggers=False)
    return logging.getLogger(__name__)


def upload_files():
    logger.info('*** Uploadding STARTED')
    files = [f for f in os.listdir(RTF_DIR) if f.endswith('.rtf')]
    logger.info('Found %s "rtf" files in dir %s', len(files), RTF_DIR)
    for file in files:
        file_location = os.path.join(RTF_DIR, file)
        process_file(file_location)
    logger.info('Upload process finished.')


def upload_transcripts():
    logger.info('*** Uploadding STARTED')
    files = [f for f in os.listdir(TRANSCRIPTS_DIR) if f.endswith('.rtf')]
    logger.info('Found %s "rtf" files in dir %s', len(files), TRANSCRIPTS_DIR)
    for file in files:
        file_location = os.path.join(TRANSCRIPTS_DIR, file)
        process_file(file_location, is_transcript=True)
    logger.info('Upload process finished.')


def run_counts():
    logger.info('*** Starting counts')
    file_path = 'input_file.xlsx'
    if not os.path.exists(file_path):
        logger.warning('Filename %s not found', file_path)
        return None
    df_input = pd.read_excel(file_path)
    df_output = pd.DataFrame()
    index2 = 1
    for i in df_input.index:
        gvkey = str(df_input.at[i, 'gvkey']).rstrip('.0').lstrip('0')
        # date = df.at[i, 'date'].date()
        # print(gvkey, date)
        articles = get_articles(gvkey)
        if len(articles) > 0:
            for article in articles:
                df_output.at[index2, 'gvkey'] = gvkey
                df_output.at[index2, 'co_name'] = df_input.at[i, 'co_name']
                df_output.at[index2, 'factiva_code'] = df_input.at[i, 'factiva_code']
                date = validate_date(article.PD)
                df_output.at[index2, 'date'] = pd.to_datetime(date)
                df_output.at[index2, 'news_count'] = float(len(article.article_ids))
                categories = []
                word_count = 0
                positive = 0
                negative = 0
                uncertain = 0
                for j, article_id in enumerate(article.article_ids):
                    logger.info('Getting data for article %s', article_id)
                    categories.append(article.main_cats[j])
                    categories.append(article.sub_cats[j])
                    analysis_data = get_analysis(article_id)
                    if analysis_data is not None:
                        word_count += analysis_data.word_count
                        positive += analysis_data.positive
                        negative += analysis_data.negative
                        uncertain += analysis_data.uncertainty
                    else:
                        df_output.at[index2, 'no_sentient'] = 'Yes'
                df_output.at[index2, 'word_count'] = float(word_count)
                df_output.at[index2, 'positive'] = float(positive)
                df_output.at[index2, 'negative'] = float(negative)
                df_output.at[index2, 'uncertain'] = float(uncertain)
                if positive == 0.0 and negative == 0.0 and uncertain == 0.0:
                    df_output.at[index2, 'no_sentient'] = 'Yes'
                categories = set(categories)
                for category in categories:
                    if category is not None and len(category.strip()) > 0:
                        category = slugify(category)
                        df_output.at[index2, category] = 'Yes'
                # print(df_output.loc[index2])
                index2 += 1
    try:
        df_output.to_csv('output.csv')
        logger.info('CSV file exported.')
    except Exception:
        logger.warning('Could not export CSV file.')
        logger.exception('message')
    try:
        df_output.to_stata('output.dta', write_index=False)
        logger.info('DTA file exported.')
    except Exception:
        logger.warning('Could not export DTA file.')
        logger.exception('message')
    logger.info('*** Finished counts')


logger = create_logger()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Managing factiva articles with database.')
    parser.add_argument(
        '-u',
        '--upload',
        help='Upload files from folder', action='store_true'
    )
    parser.add_argument(
        '-ut',
        '--upload_transcripts',
        help='Upload trancsript files from folder', action='store_true'
    )
    parser.add_argument(
        '-a',
        '--analyze',
        help='Run text analyze in articles in database', action='store_true'
    )
    parser.add_argument(
        '-c',
        '--counts',
        help='Export counts from database', action='store_true'
    )
    args = parser.parse_args()
    if args.upload: 
        upload_files()
    if args.analyze:
        analyze_artices()
    if args.counts:
        run_counts()
    if args.upload_transcripts:
        upload_transcripts()
