import json

from tweepy.streaming import StreamListener
from tweepy import Stream, OAuthHandler
import couchdbkit
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


def main():
    auth = OAuthHandler(settings.consumer_key,
                        settings.consumer_secret)
    auth.set_access_token(settings.access_token,
                          settings.access_secret)

    server = couchdbkit.Server()
    db = server[settings.database]

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