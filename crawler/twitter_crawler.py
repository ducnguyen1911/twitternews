import tweepy

__author__ = 'duc07'

# call APIs, note: due to limitation in size of results -> maybe have to call several times

# check HTTP code and handle appropriately

# check rate-limit of calling API: 150/350

import csv
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

ckey = '709q68exdKyMs4WrdBV08w'  # 'xWSJ00HHasfaHP8YDvmhCmTdqA'
csecret = 'UGMRqIWZQfHYN76oJBCVyHmrorjRUNdFJBBF41Qff8'   # 'eF3oTgafZUs7ZCTHXyaI7g2krrpvf2LaWf6sSIlQaww'
atoken = '52607422-wi0wKwdOJcbk4RDS7oYS9QIykht2QIOUF5HIo4szR'  # '1401204486-k0fGslaW87Op0MsPYYi2vcstRj0s1HNhVyDSKAB44P'
asecret = 'yaPDMTdnImz9hGqEp5V5LPtLyla5HJdALbFyHNd1x1iWV'  # 'Pi60VAcdaby409frT61gvllsYixNhZassDimklSb9Y3F8'

class listener(StreamListener):

    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status
print 'start'

# Open/Create a file to append data
csvFile = open('result.csv', 'a')
#Use csv Writer
csvWriter = csv.writer(csvFile)

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
# twitterStream = Stream(auth, listener(), timeout=60)
#
#
# for tweet in tweepy.Cursor(twitterStream.sample(), lang="en").items(10):
#     #Write a row to the csv file/ I use encode utf-8
#     csvWriter.writerow([tweet.created_at, tweet.text.encode('utf-8')])
#     print tweet.created_at, tweet.text
# csvFile.close()


# str = twitterStream.sample()


# from datetime import datetime
# print 'Start time: ', str(datetime.now())
# twitterStream.filter(track=["testtweepy12341234"])
# print 'End time: ', str(datetime.now())

api = tweepy.API(auth)
print api.get_status(86383662232375296)
# user = api.get_user('anhducdb07')
# print user.screen_name
# print user.followers_count
# for friend in user.friends():
#     print friend.screen_name

# public_tweets = tweepy.api.public_timeline()
# for tweet in public_tweets:
#     print tweet.text

# user = tweepy.api.get_user('twitter')
# print user.screen_name
# print user.followers_count
# for friend in user.friends():
#    print friend.screen_name

print 'end'