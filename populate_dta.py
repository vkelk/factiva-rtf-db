import re
import pandas as pd

from db_helper import Session, Articles, CompanyArticle, Analysis


file_path = 'sample_file.dta'


def get_articles(gvket, date):
    session = Session()
    q = session.query(CompanyArticle) \
        .join(Articles, Articles.id == CompanyArticle.article_id) \
        .filter(CompanyArticle.gvkey == gvkey) \
        .filter(Articles.PD == date)
    return q.all()


def get_analysis(article_id):
    session = Session()
    q = session.query(Analysis).filter(Analysis.id == article_id)
    if q is not None:
        return q.first()
    return None


def slugify(s):
    return re.sub('[^\w]+', '_', s).strip().lower()[:32]


if __name__ == '__main__':
    df = pd.read_stata(file_path)
    # df.to_csv('output1.csv')
    # exit()
    # df_output = pd.DataFrame()
    # print(df.head())
    for i in df.index:
        # print(df.iloc[i])
        # exit()
        gvkey = str(df.at[i, 'gvkey']).rstrip('.0')
        date = df.at[i, 'date'].date()
        print(gvkey, date)
        articles = get_articles(gvkey, date)
        if len(articles) > 0:
            df.at[i, 'news_count'] = len(articles)
            categories = []
            word_count = 0
            positive = 0
            negative = 0
            uncertain = 0
            for article in articles:
                categories.append(article.main_category)
                categories.append(article.sub_category)
                analysis_data = get_analysis(article.article_id)
                if analysis_data is not None:
                    word_count += analysis_data.word_count
                    positive += analysis_data.positive
                    negative += analysis_data.negative
                    uncertain += analysis_data.uncertainty
            df.at[i, 'word_count'] = word_count
            categories = set(categories)
            for category in categories:
                if category is not None and len(category.strip()) > 0:
                    category = slugify(category)
                    df.at[i, category] = 'Yes'
            print(df.loc[i])
    df.to_stata('output.dta', write_index=False)
