import re

from cleanco import prepare_terms, basename
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
import sparse_dot_topn.sparse_dot_topn as ct


terms = prepare_terms()


def normalize(string):
    # string = fix_text(string) # fix text encoding issues
    string = string.encode("ascii", errors="ignore").decode()  # remove non ascii chars
    string = string.lower()  # make lower case
    chars_to_remove = [")", "(", ".", "|", "[", "]", "{", "}", "'"]
    rx = '[' + re.escape(''.join(chars_to_remove)) + ']'
    string = re.sub(rx, '', string)  # remove the list of chars defined above
    string = string.replace('&', 'and')
    string = string.replace(',', ' ')
    string = string.replace('-', ' ')
    string = string.title()  # normalise case - capital at start of each word
    string = re.sub(' +', ' ', string).strip()  # get rid of multiple spaces and replace with a single space
    string = ' ' + string + ' '  # pad names for ngrams...
    return string


def ngrams(string, n=3):
    string = re.sub(r'[,-./]|\sBD', r'', normalize(string))
    ngrams = zip(*[string[i:] for i in range(n)])
    return [''.join(ngram) for ngram in ngrams]


def awesome_cossim_top(A, B, ntop, lower_bound=0):
    # force A and B as a CSR matrix.
    # If they have already been CSR, there is no overhead
    A = A.tocsr()
    B = B.tocsr()
    M, _ = A.shape
    _, N = B.shape

    idx_dtype = np.int32

    nnz_max = M*ntop

    indptr = np.zeros(M+1, dtype=idx_dtype)
    indices = np.zeros(nnz_max, dtype=idx_dtype)
    data = np.zeros(nnz_max, dtype=A.dtype)

    ct.sparse_dot_topn(
        M, N, np.asarray(A.indptr, dtype=idx_dtype),
        np.asarray(A.indices, dtype=idx_dtype),
        A.data,
        np.asarray(B.indptr, dtype=idx_dtype),
        np.asarray(B.indices, dtype=idx_dtype),
        B.data,
        ntop,
        lower_bound,
        indptr, indices, data)

    return csr_matrix((data, indices, indptr), shape=(M, N))


def get_matches_df(sparse_matrix, name_vector, top=None):
    non_zeros = sparse_matrix.nonzero()

    sparserows = non_zeros[0]
    sparsecols = non_zeros[1]

    if top:
        nr_matches = top
    else:
        nr_matches = sparsecols.size

    left_side = np.empty([nr_matches], dtype=object)
    right_side = np.empty([nr_matches], dtype=object)
    similairity = np.zeros(nr_matches)

    for index in range(0, nr_matches):
        left_side[index] = name_vector[sparserows[index]]
        right_side[index] = name_vector[sparsecols[index]]
        similairity[index] = sparse_matrix.data[index]

    return pd.DataFrame({'left_side': left_side,
                        'right_side': right_side,
                        'similairity': similairity})


if __name__ == '__main__':
    pd.set_option('display.max_colwidth', None)
    df = pd.read_csv('coname.csv')
    df.drop(columns=['id'], inplace=True)
    df.drop_duplicates('co_name', inplace=True)
    for i, row in df.iterrows():
        cleanco = basename(row['co_name'], terms, prefix=False, middle=False, suffix=True).strip()
        cleanco_norm = cleanco.lower().title()
        sql = f"UPDATE transcriptsv2.articles SET co_name_cleanco = '{cleanco_norm}' where co_name = '{row['co_name']}';"
        df.at[i, 'cleanco_normalized'] = cleanco_norm
        df.at[i, 'query'] = sql
    
    df.to_csv('co_names_variants.csv')
    sql = df['query']
    sql.to_csv('queries.sql', header=False, index=False)
    print(df.head(25))

    exit()
    co_name = df['co_name']
    co_name.drop_duplicates(inplace=True)
    for index, row in df.iterrows():

        name = basename(row['co_name'], terms, prefix=False, middle=False, suffix=True)
        print(row['co_name'], normalize(row['co_name']), name)
        exit()

    vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams)
    tf_idf_matrix = vectorizer.fit_transform(co_name)

    #  Top 200 with similarity above 0.8
    matches = awesome_cossim_top(tf_idf_matrix, tf_idf_matrix.transpose(), 200, 0.9)

    # store the  matches into new dataframe called matched_df and printing samples
    matches_df = get_matches_df(matches, co_name)
    matches_df = matches_df[matches_df['similairity'] < 0.99999]  # For removing all exact matches
    
    matches_df.sort_values('left_side', inplace=True)
    matches_df.to_csv('matches.csv')
