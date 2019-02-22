import pysentiment as ps
from factiva.models import Articles, Session


hiv4 = ps.HIV4()
lm = ps.LM()


if __name__ == '__main__':
    session = Session()
    articles = session.query(Articles)
    i = 0
    for article in articles:
        text = article.text.rstrip('None')
        tokens_hiv4 = hiv4.tokenize(text)
        score_hiv4 = hiv4.get_score(tokens_hiv4)
        tokens_lm = lm.tokenize(text)
        score_lm = lm.get_score(tokens_lm)
        print('Article id:', article.id)
        print('HIV4:', score_hiv4)
        print('LM:', score_lm)
        i += 1
        if i > 10:
            exit()
