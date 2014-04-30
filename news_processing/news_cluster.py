import couchdb
from crawler import settings
import logging, gensim, bz2
from gensim import corpora, models, similarities
from itertools import chain
import cPickle as pickle
from spam_filter import fisher

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


# retweet_count
# favorite_count
# retweeted_status.retweet_count
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



def lda_train():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    id2word, mm, tweets = load_corpus(66000)  # , start_time='2014-03-17T00:00:00', end_time='2014-04-17T23:59:59')
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

    # # Assigns the topics to the documents in corpus
    # lda_corpus = [lda[d] for d in mm]
    # # lda_corpus = lda[mm]
    # # cluster1 = []
    # # for i,j in zip(lda_corpus,documents):
    # #     if i[0][1] > 1:
    # #         print '1'
    # full_lda_corpus = []
    # for d in lda_corpus:
    #     try:
    #         d = gensim.matutils.sparse2full(d, 100)
    #         full_lda_corpus.append(d)  # check order of documents
    #     except:
    #         print 'error: ', d
    #
    # # Find the threshold, let's set the threshold to be 1/#clusters,
    # # To prove that the threshold is sane, we average the sum of all probabilities:
    # scores = list(chain(*[[score for topic, score in topic] \
    #                       for topic in [doc for doc in lda_corpus]]))
    # threshold = sum(scores)/len(scores)
    # threshold *= 3
    # print 'threshold = ', threshold
    # print '--------------------------------------------'
    #
    # cluster1 = [j for i, j in zip(full_lda_corpus, documents) if i[0] > threshold]
    # cluster2 = [j for i, j in zip(full_lda_corpus, documents) if i[1] > threshold]
    # cluster3 = [j for i, j in zip(full_lda_corpus, documents) if i[2] > threshold]
    # # cluster3 = [j for i, j in zip(full_lda_corpus, documents) if i[2][1] > threshold]
    #
    # print 'cluster1: '
    # for t in cluster1:
    #     print t, '\n'
    # print 'cluster2: '
    # for t in cluster2:
    #     print t, '\n'
    # print 'cluster3: '
    # for t in cluster3:
    #     print t, '\n'


def hdp_train():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    id2word, mm, documents = load_corpus(1000)
    # extract 100 LDA topics, using 1 pass and updating once every 1 chunk (10,000 documents)
    # lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=100,
    #                                       update_every=1, chunksize=100, passes=1)
    hdp = gensim.models.hdpmodel.HdpModel(mm, id2word)
    # print the most contributing words for 20 randomly selected topics
    hdp.print_topics(100)


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

    # cl = fisher.fisherclassifier(fisher.getWords)
    # cl.setdb('test1.db')
    # cl.setminimum('false', 0.67)
    # cl.setminimum('true', 0.1)

    results = []
    i = 0

    if _start_time is not None:
        for doc in couchdb_pager(db, view_name='doc_duc/view_create_at',
                                 startkey=_start_time, endkey=_end_time,
                                 bulk=_numb_tweets):
            # print '--> ', doc, ' - ', db[doc]['text']
            # results.append(db[doc]['text'])
            # text = db[doc]['text']
            # print(text)
            # text = text.replace("'", "")
            # text = text.replace('"', '')
            # cl_result = cl.classify(db[doc]['text'])
            # print cl_result
            # if cl_result == 'true':
            results.append(db[doc])  # append all properties of tweets
            i += 1
            if i == _numb_tweets:
                break
    else:
        for doc in couchdb_pager(db, bulk=_numb_tweets):
            # print '--> ', doc, ' - ', db[doc]['text']
            # results.append(db[doc]['text'])
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
    tweets = retrieve_tweets(settings.database_geo, _number_tweets, _start_time=start_time, _end_time=end_time)
    texts = get_texts(tweets)
    texts = clean(texts)
    dictionary = corpora.Dictionary(texts)
    # dictionary = corpora.HashDictionary(texts, id_range=100000)
    dictionary.save('/tmp/hashDict.dict')
    corpus = [dictionary.doc2bow(text) for text in texts]

    # load id->word mapping (the dictionary), one of the results of step 2 above
    # id2word = dictionary  # gensim.corpora.Dictionary.load_from_text('wiki_en_wordids.txt')

    # load corpus iterator
    # mm = corpus  # gensim.corpora.MmCorpus('wiki_en_tfidf.mm')
    return dictionary, corpus, tweets


def load_model():
    return models.LdaModel.load('/tmp/model.lda')


def load_dict():
    return corpora.HashDictionary.load('/tmp/hashDict.dict')


def remove_frequent_words(texts):
    results = []

    # high_df_words = {}
    # high_f_words = {}
    # for doc in texts:
    #     flag = {}
    #     for word in doc:
    #         if word not in flag.keys():
    #             if word not in high_df_words.keys():
    #                 high_df_words[word] = 1
    #             else:
    #                 high_df_words[word] += 1
    #             flag[word] = 1
    #         if word not in high_f_words.keys():
    #             high_f_words[word] = 1
    #         else:
    #             high_f_words[word] += 1
    #     flag = {}
    #
    # for w in sorted(high_df_words, key=high_df_words.get, reverse=False):
    #     print w, high_df_words[w]
    # f_high_words = [w for w in high_df_words.keys() if high_df_words[w] > 64]
    # pickle.dump(f_high_words, open("high_words.p", "wb"))

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


def get_tweets_in_topic():
    print ''


def main_process(_db_name, _bulk_size):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    server = couchdb.Server()
    db = server[_db_name]
    tweet_bulk = []
    lda_model = load_model()
    i = 0
    j = 0
    for doc in couchdb_pager(db, bulk=_bulk_size):
        # print '--> ', doc, ' - ', db[doc]['text']
        tweet_bulk.append(db[doc]['text'])
        i += 1
        if i == _bulk_size:
            j += 1
            print 'Load enough tweets.----------------------------------'
            # process bulk of tweets
            tweet_bulk = clean(tweet_bulk)
            dict = load_dict()
            new_corpus = [dict.doc2bow(tweet) for tweet in tweet_bulk]
            print 'Update LDA model ----------------------------------'
            lda_model.update(new_corpus)
            print 'Print topics: ----------------------------------'
            lda_model.print_topics(30)
            # save list of topics + related tweets to a pickle file or DB -> GUI load results later
            get_topics(lda_model,)
            # reset
            # tweet_bulk = []
            i = 0
            if j == 1:
                return tweet_bulk
    return tweet_bulk


def main():
    lda_train()
    # hdp()
    # main_process(settings.database_geo, 1000)
    # retrieve_tweets(_db_name=settings.database_us, _numb_tweets=3000,
    #                 _start_time='2014-04-11T00:00:00', _end_time='2014-04-11T23:59:59')

    # from sklearn.feature_extraction.text import CountVectorizer
    # vectorizer = CountVectorizer(min_df=1)
    # corpus = [
    #     'This is the first document.',
    #     'This is the second second document.',
    #     'And the third one.',
    #     'Is this the first document?',
    # ]
    # X = vectorizer.fit_transform(corpus)
    # print vectorizer.vocabulary_.get('document')

if __name__ == "__main__":
    main()