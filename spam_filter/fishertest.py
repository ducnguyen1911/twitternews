import fisher

print "step 1"
cl=fisher.fisherclassifier(fisher.getWords)
print "step 2"
cl.setdb('test2.db')
print "step 3"
#fisher.filetrain(cl)
#print cl2.retrieve_tweets_classify(2)
#cl2.setthreshold('false', 0.67)
#cl2.setthreshold('true', 0.1)
#cl.setminimum('false',0.9)
cl.setminimum('false',0.1)
cl.setminimum('true',0.9)
#print cl.classify('@SydneyZagger SWAG! REALNESS! NEVER STRUGGLIN!')
good_tweets = cl.retrieve_tweets_classify(20)
print('Start to print good tweets')
for t in good_tweets:
    print '-------------', t['text']
print "step 4"
