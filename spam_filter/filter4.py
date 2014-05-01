import re
from pysqlite2 import dbapi2 as sqlite
import couchdb


def getWords(doc):
    splitter = re.compile('\\W*')
    # Split the words by non-alpha characters
    words = [s.lower() for s in splitter.split(doc)
             if len(s) > 2 and len(s) < 20]

    # Return the unique set of words only
    return dict([(w, 1) for w in words])

def filetrain(cl):
    count = 1

    dataset = open('output.txt', 'r')

    for line in dataset:
        if count % 2 != 0:
            	content = line
            	#content2 = content.replace("'", "")
		#content2 = line.replace("'", "")
            	count += 1
        else:
            	tag = line
            	print content
            	print tag
            	cl.train(content, tag)
            	count += 1

        print count

def sampletrain(cl):
    cl.train('Nobody owns the water.','good')
    cl.train('the quick rabbit jumps fences','good')
    cl.train('buy pharmaceuticals now','bad')
    cl.train('make quick money at the online casino','bad')
    cl.train('the quick brown fox jumps','good')

class classifier:
    def __init__(self,getfeatures,filename=None):
        # Counts of feature/category combinations
        self.fc={}
        # Counts of documents in each category
        self.cc={}
        self.getfeatures=getfeatures
        #classifier.__init__(self,getfeatures)
        self.thresholds={}

    def setdb(self,dbfile):
        self.con=sqlite.connect(dbfile)
        self.con.execute('create table if not exists fc(feature,category,count)')
        self.con.execute('create table if not exists cc(category,count)')

    def setthreshold(self,cat,t):
        self.thresholds[cat]=t

    def getthreshold(self,cat):
        if cat not in self.thresholds: return 1.0
        return self.thresholds[cat]

    def incf(self,f,cat):
        count=self.fcount(f,cat)
        if count==0:
            self.con.execute("insert into fc values ('%s','%s',1)"
                       % (f,cat))
        else:
            self.con.execute(
                "update fc set count=%d where feature='%s' and category='%s'"
                % (count+1,f,cat))

    # Increase the count of a category
    def incc(self,cat):
        count=self.catcount(cat)
        if count==0:
            self.con.execute("insert into cc values ('%s',1)" % (cat))
        else:
            self.con.execute("update cc set count=%d where category='%s'"
                       % (count+1,cat))

    # The number of times a feature has appeared in a category
    def fcount(self,f,cat):
        res=self.con.execute(
            'select count from fc where feature="%s" and category="%s"'
             %(f,cat)).fetchone(  )
        if res==None: return 0
        else: return float(res[0])

    # The number of items in a category
    def catcount(self,cat):
        res=self.con.execute('select count from cc where category="%s"'
                         %(cat)).fetchone(  )
        if res==None: return 0
        else: return float(res[0])

    # The total number of items
    def totalcount(self):
        res=self.con.execute('select sum(count) from cc').fetchone(  );
        if res==None: return 0
        return res[0]

    # The list of all categories
    def categories(self):
        cur=self.con.execute('select category from cc');
        return [d[0] for d in cur]

    def train(self,item,cat):
        features=self.getfeatures(item)
        # Increment the count for every feature with this category
        for f in features:
            self.incf(f,cat)

        # Increment the count for this category
        self.incc(cat)

        self.con.commit(  )

    def fprob(self,f,cat):
        if self.catcount(cat)==0: return 0
        # The total number of times this feature appeared in this
        # category divided by the total number of items in this category
        return self.fcount(f,cat)/self.catcount(cat)

    def weightedprob(self,f,cat,prf,weight=1.0,ap=0.5):
        # Calculate current probability
        basicprob=prf(f,cat)

        # Count the number of times this feature has appeared in
        # all categories
        totals=sum([self.fcount(f,c) for c in self.categories(  )])

        # Calculate the weighted average
        bp=((weight*ap)+(totals*basicprob))/(weight+totals)
        return bp

    def classify(self,item,default=None):
        probs={}
        # Find the category with the highest probability
        max=0.0

        for cat in self.categories(  ):
            probs[cat]=self.prob(item,cat)

            if probs[cat]>max:
                max=probs[cat]
                best=cat

        # Make sure the probability exceeds threshold*next best
        for cat in probs:
            if cat==best: continue
            if probs[cat]*self.getthreshold(best)>probs[best]: return default
        return best


    def couchdb_pager(self, db, view_name='_all_docs',
                  startkey=None, startkey_docid=None,
                  endkey=None, endkey_docid=None, bulk=5000):
        # Request one extra row to resume the listing there later.
        options = {'limit': bulk + 1}
        if startkey:
            options['startkey'] = startkey
            if startkey_docid:
                options['startkey_docid'] = startkey_docid
        if endkey:
            options['endkey'] = endkey
            if endkey_docid:
                options['endkey_docid'] = endkey_docid
        done = False
        while not done:
            view = db.view(view_name, **options)
            rows = []
            # If we got a short result (< limit + 1), we know we are done.
            if len(view) <= bulk:
                done = True
                rows = view.rows
            else:
                # Otherwise, continue at the new start position.
                rows = view.rows[:-1]
                last = view.rows[-1]
                options['startkey'] = last.key
                options['startkey_docid'] = last.id

            for row in rows:
                yield row.id

    def retrieve_tweets_classify(self,_numb_tweets):
        server = couchdb.Server()
        db = server["tweets_us"]

        results = []
        i = 0
        for doc in self.couchdb_pager(db):
            # print '--> ', doc, ' - ', db[doc]['text']
            try:
                if self.classify(db[doc]['text']) == 'true':
                    results.append(db[doc])
                    i += 1
                    if i == _numb_tweets:
                        break
            except:
                print 'error'
        return results


class naivebayes(classifier):
    def docprob(self,item,cat):
        features=self.getfeatures(item)

        # Multiply the probabilities of all the features together
        p=1
        for f in features: p*=self.weightedprob(f,cat,self.fprob)
        return p

    def prob(self,item,cat):
        catprob=self.catcount(cat)/self.totalcount(  )
        docprob=self.docprob(item,cat)
        return docprob*catprob



