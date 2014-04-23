import fisher

print "step 1"
cl=fisher.fisherclassifier(fisher.getWords)
print "step 2"
cl.setdb('test1.db')
print "step 3"
#print cl2.retrieve_tweets_classify(2)
#cl2.setthreshold('false', 0.67)
#cl2.setthreshold('true', 0.1)
#cl.setminimum('false',0.9)
cl.setminimum('false',0.67)
cl.setminimum('true',0.1)
#print cl.classify('There was a critical bug in OpenSSL discovered on Monday. Change passwords for the main online sites that you use. #heartbleed')
print cl.retrieve_tweets_classify(20)
print "step 4"
