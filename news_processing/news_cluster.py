import couchdb
from crawler import settings
import logging, gensim, bz2
from gensim import corpora, models, similarities
from itertools import chain

__author__ = 'duc07'


class TweetCluster:
    # threshold = 1

    def __init__(self):
        print 'self'

def couchdb_pager(db, view_name='_all_docs',
                  startkey=None, startkey_docid=None,
                  endkey=None, endkey_docid=None, bulk=5000):
    # Request one extra row to resume the listing there later.
    options = {'limit': bulk + 1}
    if startkey:
        options['startkey'] = startkey
        if startkey_docid:
            options['startkey_docid'] = startkey_docid
    if endkey:
        options['endkey'] = endkey
        if endkey_docid:
            options['endkey_docid'] = endkey_docid
    done = False
    while not done:
        view = db.view(view_name, **options)
        rows = []
        # If we got a short result (< limit + 1), we know we are done.
        if len(view) <= bulk:
            done = True
            rows = view.rows
        else:
            # Otherwise, continue at the new start position.
            rows = view.rows[:-1]
            last = view.rows[-1]
            options['startkey'] = last.key
            options['startkey_docid'] = last.id

        for row in rows:
            yield row.id


def retrieve_tweets(_db_name, _numb_tweets):
    server = couchdb.Server()
    db = server[_db_name]

    results = []
    i = 0
    for doc in couchdb_pager(db):
        # print '--> ', doc, ' - ', db[doc]['text']
        results.append(db[doc]['text'])
        i += 1
        if i == _numb_tweets:
            break
    return results


def clean_doc(documents):
    # remove common words and tokenize
    stoplist = set('rt for a of the and to in i my me you your this'.split())
    texts = [[word for word in document.lower().split() if word not in stoplist]
             for document in documents]

    # remove words that appear only once
    all_tokens = sum(texts, [])
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
    texts = [[word for word in text if word not in tokens_once]
             for text in texts]
    return texts


def load_corpus(_number_tweets):
    documents = retrieve_tweets(settings.database, _number_tweets)
    texts = clean_doc(documents)
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    # load id->word mapping (the dictionary), one of the results of step 2 above
    id2word = dictionary  # gensim.corpora.Dictionary.load_from_text('wiki_en_wordids.txt')

    # load corpus iterator
    mm = corpus  # gensim.corpora.MmCorpus('wiki_en_tfidf.mm')
    return id2word, mm, documents


def lsa():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    id2word, mm, documents = load_corpus(10000)
    lsa = gensim.models.lsimodel.LsiModel(corpus=mm, id2word=id2word, num_topics=100)
    # print the most contributing words for 100 randomly selected topics
    lsa.print_topics(100)


def lda():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    id2word, mm, documents = load_corpus(2000)
    # extract 100 LDA topics, using 1 pass and updating once every 1 chunk (10,000 documents)
    lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=100,
                                          update_every=1, chunksize=100, passes=1)
    # print the most contributing words for 20 randomly selected topics
    lda.print_topics(100)

    # Assigns the topics to the documents in corpus
    lda_corpus = [lda[d] for d in mm]
    # lda_corpus = lda[mm]
    # cluster1 = []
    # for i,j in zip(lda_corpus,documents):
    #     if i[0][1] > 1:
    #         print '1'
    full_lda_corpus = []
    for d in lda_corpus:
        try:
            d = gensim.matutils.sparse2full(d, 100)
            full_lda_corpus.append(d)  # check order of documents
        except:
            print 'error: ', d

    # Find the threshold, let's set the threshold to be 1/#clusters,
    # To prove that the threshold is sane, we average the sum of all probabilities:
    scores = list(chain(*[[score for topic, score in topic] \
                          for topic in [doc for doc in lda_corpus]]))
    threshold = sum(scores)/len(scores)
    print 'threshold = ', threshold
    print '--------------------------------------------'

    cluster1 = [j for i, j in zip(full_lda_corpus, documents) if i[0] > threshold]
    cluster2 = [j for i, j in zip(full_lda_corpus, documents) if i[1] > threshold]
    cluster3 = [j for i, j in zip(full_lda_corpus, documents) if i[2] > threshold]
    # cluster3 = [j for i, j in zip(full_lda_corpus, documents) if i[2][1] > threshold]

    print 'cluster1: '
    for t in cluster1:
        print t, '\n'
    print 'cluster2: '
    for t in cluster2:
        print t, '\n'
    print 'cluster3: '
    for t in cluster3:
        print t, '\n'


def main():
    lda()

if __name__ == "__main__":
    main()