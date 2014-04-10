import json

from tweepy.streaming import StreamListener
from tweepy import Stream, OAuthHandler
import couchdb
import settings
import time
import sys


class CouchDBStreamListener(StreamListener):
    def __init__(self, db):
        self.db = db
        self.tweet_count = 0
        self.received_friend_ids = False

    def on_data(self, data):
        try:
            tweet = json.loads(data)
        except Exception:
            print("Failed to parse tweet data")
            tweet = None

        if tweet:
            if tweet.has_key('id') and tweet.has_key("text") and tweet['lang'] == 'en' \
                and tweet['coordinates'] is not None:
                print("Tweet --> %s: %s" % (tweet['user']['screen_name'], tweet['text']))

                tweet['doc_type'] = "tweet"

                self.db["tweet:%d" % tweet['id']] = tweet

                self.tweet_count += 1
            elif not self.received_friend_ids and tweet.has_key("friends"):
                print("Got %d user ids" % len(tweet['friends']))
                self.received_friend_ids = True
            else:
                print("Received a responce that is not a tweet")
                print tweet

        return True

    def on_exception(self, exception):
        """Called when an unhandled exception occurs."""
        print 'Inside exception handle'
        return

    def on_limit(self, track):
        """Called when a limitation notice arrvies"""
        print "!!! Limitation notice received: %s" % str(track)
        return

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        time.sleep(10)
        return True


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

    documents = retrieve_tweets(50000)
    texts = clean_doc(documents)
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    # load id->word mapping (the dictionary), one of the results of step 2 above
    id2word = dictionary  # gensim.corpora.Dictionary.load_from_text('wiki_en_wordids.txt')

    # load corpus iterator
    mm = corpus  # gensim.corpora.MmCorpus('wiki_en_tfidf.mm')

    # extract 100 LDA topics, using 1 pass and updating once every 1 chunk (10,000 documents)
    lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=100,
                                          update_every=1, chunksize=100, passes=1)

    # print the most contributing words for 20 randomly selected topics
    lda.print_topics(100)

    # a trained model can used be to transform new, unseen documents
    # (plain bag-of-words count vectors) into LDA topic distributions:
    # doc_bow = "new doc"
    # doc_lda = lda[doc_bow]


def main():
    auth = OAuthHandler(settings.consumer_key,
                        settings.consumer_secret)
    auth.set_access_token(settings.access_token,
                          settings.access_secret)

    server = couchdb.Server()
    db = server[settings.database_geo]

    # lsa()

    listener = CouchDBStreamListener(db)

    stream = Stream(auth, listener)
    while True:
        if listener.tweet_count > 100000:
            break
        try:
            # stream.userstream()
            stream.sample()
        except Exception as e:
            print 'error: ', e
            print("Total tweets received: %d" % listener.tweet_count)


if __name__ == "__main__":
    main()