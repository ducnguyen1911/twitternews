import filter4

print "step 1"
cl2=filter4.naivebayes(filter4.getWords)
print "step 2"
cl2.setdb('test1.db')
print "step 3"
#print cl2.retrieve_tweets_classify(2)
cl2.setthreshold('false', 0.9)
cl2.setthreshold('true', 0.1)
print cl2.classify('North Carolina prosecutor was original target in kidnapping plot father abducted by mistake')
print "step 4"
