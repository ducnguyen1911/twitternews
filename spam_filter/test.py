import filter3

cl2=filter3.naivebayes(filter3.getWords)
cl2.setdb('test1.db')
filter3.filetrain(cl2)
print cl2.classify('quick money')
