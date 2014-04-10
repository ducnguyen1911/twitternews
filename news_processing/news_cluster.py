import couchdb
from crawler import settings

__author__ = 'duc07'


class TweetCluster:
    # threshold = 1

    def __init__(self):
        print 'self'

    # def calc_lsh(self):
    #     print 'calculate LSH'
    #
    # def get_set_collide(self, _doc):
    #     print 'return set of colliding documents for a given document using LSH'
    #
    # def cluster(self, _clusters, _doc):
    #     # format: _clusters: {cluster1: [center1, [doc1, doc2, doc3,...]], cluster2: [], cluster3: []}
    #     # format: _doc: {term1: tfidf1, term2: tfidf2}
    #     if len(_clusters) == 0:
    #         # no cluster
    #         print 'no cluster'
    #     else:
    #         min_dist = 10000
    #         min_cluster = ''
    #         for name, cluster in _clusters.iteritems():
    #             centroid = cluster[0]
    #             if self.distance(centroid, _doc) < min_dist:
    #                 min_cluster = name
    #         # assign _doc to cluster with min distance
    #         _clusters[min_cluster][1].append(_doc)
    #         self.update_cluster(_clusters[min_cluster])
    #
    #
    # def distance(self, _doc1, _doc2):
    #     return 0
    #
    # def update_cluster(self, _cluster):
    #     return 0

    # when new tweets come -> new vocabularies -> how update tf-idf of old tweets -> just update df of center of cluster
    # since when new tweets come, idf does not change, only df of all tweets change (and df of a term for all docs
    # are same.)

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


def retrieve_tweets(_numb_tweets):
    server = couchdb.Server()
    db = server[settings.database]

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


def lsa():
    import logging, gensim, bz2

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    from gensim import corpora, models, similarities

    documents = retrieve_tweets(1000)
    texts = clean_doc(documents)
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    # load id->word mapping (the dictionary), one of the results of step 2 above
    id2word = dictionary  # gensim.corpora.Dictionary.load_from_text('wiki_en_wordids.txt')

    # load corpus iterator
    mm = corpus  # gensim.corpora.MmCorpus('wiki_en_tfidf.mm')

    # extract 100 LDA topics, using 1 pass and updating once every 1 chunk (10,000 documents)
    lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=10,
                                          update_every=1, chunksize=100, passes=1)

    # print the most contributing words for 20 randomly selected topics
    lda.print_topics(100)

    # a trained model can used be to transform new, unseen documents
    # (plain bag-of-words count vectors) into LDA topic distributions:
    # doc_bow = "new doc"
    # doc_lda = lda[doc_bow]


def main():
    lsa()

if __name__ == "__main__":
    main()