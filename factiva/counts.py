import re
from sqlalchemy.dialects.postgresql import array_agg
from .models import Session, Articles, CompanyArticle, Analysis


def get_articles(gvkey, date=None):
    session = Session()
    q = session.query(
            array_agg(CompanyArticle.article_id).label('article_ids'),
            array_agg(CompanyArticle.main_category).label('main_cats'),
            array_agg(CompanyArticle.sub_category).label('sub_cats'),
            Articles.PD
        ) \
        .join(Articles, Articles.id == CompanyArticle.article_id) \
        .filter(CompanyArticle.gvkey == gvkey)
    if date is not None:
        q = q.filter(Articles.PD == date)
    q = q.group_by(Articles.PD).order_by(Articles.PD)
    return q.all()


def get_analysis(article_id):
    session = Session()
    q = session.query(Analysis).filter(Analysis.id == article_id)
    if q is not None:
        return q.first()
    return None


def slugify(s):
    return re.sub('[^\w]+', '_', s).strip().lower()[:32]
