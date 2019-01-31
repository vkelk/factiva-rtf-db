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
    for i in df.index:
        gvkey = str(df.at[i, 'gvkey']).rstrip('.0')
        date = df.at[i, 'date'].date()
        print(gvkey, date)
        articles = get_articles(gvkey, date)
        if len(articles) > 0:
            df.at[i, 'news_count'] = float(len(articles))
            categories = []
            word_count = 0
            positive = 0
            negative = 0
            uncertain = 0
            for article in articles:
                print('Getting data for article', article.article_id)
                categories.append(article.main_category)
                categories.append(article.sub_category)
                analysis_data = get_analysis(article.article_id)
                if analysis_data is not None:
                    word_count += analysis_data.word_count
                    positive += analysis_data.positive
                    negative += analysis_data.negative
                    uncertain += analysis_data.uncertainty
                else:
                    df.at[i, 'no_sentient'] = 'Yes'
            df.at[i, 'word_count'] = float(word_count)
            df.at[i, 'positive'] = float(positive)
            df.at[i, 'negative'] = float(negative)
            df.at[i, 'uncertain'] = float(uncertain)
            if positive == 0.0 and negative == 0.0 and uncertain == 0.0:
                df.at[i, 'no_sentient'] = 'Yes'
            categories = set(categories)
            for category in categories:
                if category is not None and len(category.strip()) > 0:
                    category = slugify(category)
                    df.at[i, category] = 'Yes'
            print(df.loc[i])
    try:
        df.to_csv('output.csv')
        print('CSV file exported.')
    except Exception as e:
        print('Could not export CSV file.')
        print(type(e), str(e))
    try:
        df.to_stata('output.dta', write_index=False)
        print('DTA file exported.')
    except Exception as e:
        print('Could not export DTA file.')
        print(type(e), str(e))
