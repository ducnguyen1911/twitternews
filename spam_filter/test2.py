import filter4

print "step 1"
cl2=filter4.naivebayes(filter4.getWords)
print "step 2"
cl2.setdb('test2.db')
print "step 3"
print cl2.retrieve_tweets_classify(2)
cl2.setthreshold('false', 0.1)
cl2.setthreshold('true', 2)
print cl2.classify('Gotta Keep A Gun Over Here')
print "step 4"
