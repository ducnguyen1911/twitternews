import filter


cl=filter.spamFilter(filter.getWords)
cl.train('the quick brown fox jumps over the lazy dog','good')
cl.train('make quick money in the online casino','bad')
print cl.countTimesFeatureInCategory('quick','good')

print cl.countTimesFeatureInCategory('quick','bad')