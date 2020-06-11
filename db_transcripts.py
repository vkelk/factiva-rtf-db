import argparse
from datetime import datetime
import logging
import logging.config
import os
from pprint import pprint

from factiva.models import Session, Articles
from transcripts.db_transcript import DbTranscript


logger = logging.getLogger(__name__)

session = Session()
articles = session.query(Articles.id, Articles.text_clean).all()
for article in articles:
    transcript = DbTranscript(article.text_clean)
    print(transcript.article_text)
    pprint(transcript.match_split())
    exit()