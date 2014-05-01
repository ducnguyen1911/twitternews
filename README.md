twitternews: Detect news from Twitter
===========
Source code for project of class CSCE 670 - Texas A&M University

Before running this source code, make sure you have the following libraries installed:
  + tweepy
  + couchdb
  + pysqlite2
  + gensim

Description of files in source code  :
  + utils/settings.py: set parameters of this system
  + crawler/user_stream.py: crawl tweets from Twitter
  + spam_filter/fisher.py: filter news tweets from spam tweets. It uses classification technique named Fisher model
  + news_processing/test2.db: db file to store features of Fisher classification.  
  + news_processing/news_cluster.py: cluster tweets to detect topics. It uses LDA model for topic detection.
  + ui/web.py: build web interface of this system. It uses Google Maps to display topics and tweets

 
  
  

