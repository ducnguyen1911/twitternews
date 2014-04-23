import filter4

print "step 1"
cl2=filter4.naivebayes(filter4.getWords)
print "step 2"
cl2.setdb('test1.db')
print "step 3"
print cl2.retrieve_tweets_classify(2)
print "step 4"
