import filter2

cl2=filter2.naivebayes(filter2.getWords)
cl2.setdb('test1.db')
filter2.sampletrain(cl2)
print cl2.classify('quick money')
