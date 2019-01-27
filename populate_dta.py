import pandas as pd

import settings
from db_helper import Session, Articles, Analysis, Company, CompanyArticle, sessionmaker, db_engine


file_path = 'sample_file.dta'

def get_articles(gvket, date):
    session = Session()
    q = session.query(CompanyArticle) \
        .join(Articles, Articles.id == CompanyArticle.article_id) \
        .filter(CompanyArticle.gvkey == gvkey) \
        .filter(Articles.PD == date)
    return q.all()


if __name__ == '__main__':
    df = pd.read_stata(file_path)
    for i in df.index:
        gvkey = str(df.at[i, 'gvkey']).rstrip('.0')
        date = df.at[i, 'date'].date()
        print(gvkey, date)
        articles = get_articles(gvkey, date)
        if len(articles) > 0:
            df.at[i, 'daily_articles'] = len(articles)
            categories = []
            for article in articles:
                categories.append(article.main_category)
                categories.append(article.sub_category)
            categories = set(categories)
            for category in categories:
                if len(category.trim()) > 0:
                    df.at[i, category] = 'Yes'
            print(df.loc[i])
    df.to_stata('output.dta', write_index=False)
