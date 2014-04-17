import filter2

cl = filter2.naivebayes(filter2.getWords)
filter2.sampletrain(cl)
print cl.classify('quick rabbit',default='unknown')

print cl.classify('quick money',default='unknown')

cl.setthreshold('bad',3.0)
print cl.classify('quick money',default='unknown')


