import logging
from itertools import chain
import cPickle as pickle

import couchdb
import gensim
from gensim import corpora, models

from spam_filter import fisher
from utils import settings


__author__ = 'duc07'


class TweetCluster:
    def __init__(self):
        print 'self'


def lsa_train():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    id2word, mm, documents = load_corpus(10000)
    lsa = gensim.models.lsimodel.LsiModel(corpus=mm, id2word=id2word, num_topics=100)
    # print the most contributing words for 100 randomly selected topics
    lsa.print_topics(100)


def hdp_train():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    id2word, mm, documents = load_corpus(1000)
    # extract 100 LDA topics, using 1 pass and updating once every 1 chunk (10,000 documents)
    # lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=100,
    #                                       update_every=1, chunksize=100, passes=1)
    hdp = gensim.models.hdpmodel.HdpModel(mm, id2word)
    # print the most contributing words for 20 randomly selected topics
    hdp.print_topics(100)


def lda_train():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    id2word, mm, tweets = load_corpus(1000, start_time='2014-04-15T00:00:00', end_time='2014-04-15T23:59:59')
    print 'Size of total good tweets: ', len(tweets)
    # extract 100 LDA topics, using 1 pass and updating once every 1 chunk (10,000 documents)
    lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=100,
                                          update_every=1, chunksize=1000, passes=1)
    lda.save('/tmp/model.lda')
    # print the most contributing words for 20 randomly selected topics
    lda.print_topics(100)

    ls_topics = get_topics(lda, mm, tweets, 100)
    # add geo(lat, long) for center of clusters:
    ls_topics = add_geo_center(ls_topics)
    # add ranking score for each cluster:
    ls_topics = add_ranking_score(ls_topics)
    # save to pickle file
    pickle.dump(ls_topics, open("topics.p", "wb"))
    return ls_topics


def add_geo_center(ls_topics):
    for topic in ls_topics:
        geo_center = [0, 0]  # long, lat
        i = 0
        for tweet in topic[1]:
            if tweet['coordinates']['coordinates']:
                i += 1
                geo_center[0] += tweet['coordinates']['coordinates'][0]  # long
                geo_center[1] += tweet['coordinates']['coordinates'][1]  # lat
        geo_center[0] /= i if len(topic[1]) > 0 else 0
        geo_center[1] /= i if len(topic[1]) > 0 else 0
        topic.append(geo_center)
    return ls_topics


def add_ranking_score(ls_topics):
    for topic in ls_topics:
        numb_favorite = 0
        numb_rt = 0
        numb_org_rt = 0
        for tweet in topic[1]:
            if tweet['retweet_count']:
                print 'retweet occur \n'
                numb_rt += tweet['retweet_count']
            if tweet['favorite_count']:
                print 'favorite occur \n'
                numb_favorite += tweet['favorite_count']
            if 'retweeted_status' in tweet:
                if tweet['retweeted_status']['retweet_count']:
                    numb_org_rt += tweet['retweeted_status']['retweet_count']
        topic_score = numb_favorite + numb_rt * 2 + numb_org_rt * 0.5
        topic.append(topic_score)
    return ls_topics


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


def retrieve_tweets(_db_name, _numb_tweets, _start_time=None, _end_time=None):
    server = couchdb.Server()
    db = server[_db_name]

    cl = fisher.fisherclassifier(fisher.getWords)
    cl.setdb('test2.db')
    cl.setminimum('false', 0.1)
    cl.setminimum('true', 0.9)

    results = []
    i = 0

    if _start_time is not None:
        for doc in couchdb_pager(db, view_name='doc_duc/view_create_at',
                                 startkey=_start_time, endkey=_end_time,
                                 bulk=_numb_tweets):
            cl_result = cl.classify(db[doc]['text'])
            print cl_result
            if cl_result == 'true':
                results.append(db[doc])  # append all properties of tweets
                i += 1
                if i == _numb_tweets:
                    break
    else:
        for doc in couchdb_pager(db, bulk=_numb_tweets):
            try:
                if 'text' in db[doc].keys():
                    results.append(db[doc])  # append all properties of tweets
                    i += 1
                    if i == _numb_tweets:
                        break
            except:
                print 'error'
    return results


def get_texts(tweets):
    texts = [t['text'] for t in tweets]
    return texts


def load_corpus(_number_tweets, start_time=None, end_time=None):
    tweets = retrieve_tweets(settings.database_us, _number_tweets, _start_time=start_time, _end_time=end_time)
    texts = get_texts(tweets)
    texts = clean(texts)
    dictionary = corpora.Dictionary(texts)
    # dictionary = corpora.HashDictionary(texts, id_range=100000)
    dictionary.save('/tmp/hashDict.dict')
    corpus = [dictionary.doc2bow(text) for text in texts]
    return dictionary, corpus, tweets


def load_model():
    return models.LdaModel.load('/tmp/model.lda')


def load_dict():
    return corpora.HashDictionary.load('/tmp/hashDict.dict')


def remove_frequent_words(texts):
    results = []
    f_high_words = pickle.load(open("high_words.p", "rb"))
    results = [[word for word in text if word not in f_high_words]
             for text in texts]
    return results


def clean(documents):
    # remove common words and tokenize
    stoplist = set('rt for a of the and to in i my me you your this'.split())
    texts = [[word for word in doc.lower().split() if (word not in stoplist and is_ascii(word))]
             for doc in documents]

    texts = remove_frequent_words(texts)

    # remove words that appear only once
    all_tokens = sum(texts, [])
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
    texts = [[word for word in text if word not in tokens_once]
             for text in texts]
    # remove text = []
    texts = [text for text in texts if len(text) > 0]
    # for t in texts:
    #     print t
    return texts


def is_ascii(_word):
    try:
        _word.decode('ascii')
    except:
        return False
    else:
        return True


def get_topics(_lda, _mm, _tweets, _numb_topics):
    # Assigns the topics to the documents in corpus
    lda_corpus = [_lda[d] for d in _mm]
    full_lda_corpus = []
    for d in lda_corpus:
        try:
            d = gensim.matutils.sparse2full(d, _numb_topics)
            full_lda_corpus.append(d)  # check order of documents
        except:
            print 'error: ', d

    # Find the threshold, let's set the threshold to be 1/#clusters,
    # To prove that the threshold is sane, we average the sum of all probabilities:
    scores = list(chain(*[[score for topic, score in topic] \
                          for topic in [doc for doc in lda_corpus]]))
    threshold = sum(scores)/len(scores)
    # threshold *= 3
    print 'threshold = ', threshold
    print '--------------------------------------------'

    ls_topics = _lda.show_topics(topics=-1)

    clusters = []
    for t in range(_numb_topics):
        temp = [j for i, j in zip(full_lda_corpus, _tweets) if i[t] > threshold]
        clusters.append(temp)
    clusters.reverse()
    clusters_with_topic = [[i, j] for i, j in zip(ls_topics, clusters)]
    return clusters_with_topic


# def main_process(_db_name, _bulk_size):
#     logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
#     server = couchdb.Server()
#     db = server[_db_name]
#     tweet_bulk = []
#     lda_model = load_model()
#     i = 0
#     j = 0
#     for doc in couchdb_pager(db, bulk=_bulk_size):
#         # print '--> ', doc, ' - ', db[doc]['text']
#         tweet_bulk.append(db[doc]['text'])
#         i += 1
#         if i == _bulk_size:
#             j += 1
#             print 'Load enough tweets.----------------------------------'
#             # process bulk of tweets
#             tweet_bulk = clean(tweet_bulk)
#             dict = load_dict()
#             new_corpus = [dict.doc2bow(tweet) for tweet in tweet_bulk]
#             print 'Update LDA model ----------------------------------'
#             lda_model.update(new_corpus)
#             print 'Print topics: ----------------------------------'
#             lda_model.print_topics(30)
#             # save list of topics + related tweets to a pickle file or DB -> GUI load results later
#             get_topics(lda_model,)
#             # reset
#             # tweet_bulk = []
#             i = 0
#             if j == 1:
#                 return tweet_bulk
#     return tweet_bulk


def main():
    lda_train()
    # hdp()

if __name__ == "__main__":
    main()