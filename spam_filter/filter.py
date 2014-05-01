import re
import math


def getWords(doc):
    splitter = re.compile('\\W*')
    # Split the words by non-alpha characters
    words = [s.lower() for s in splitter.split(doc)
             if len(s) > 2 and len(s) < 20]

    # Return the unique set of words only
    return dict([(w, 1) for w in words])

def sampletrain(cl):
    cl.train('Nobody owns the water.','good')
    cl.train('the quick rabbit jumps fences','good')
    cl.train('buy pharmaceuticals now','bad')
    cl.train('make quick money at the online casino','bad')
    cl.train('the quick brown fox jumps','good')


class spamFilter:
    def __init__(self, getfeatures, filename=None):

        self.featureCount = {}
        self.categoryCount = {}
        self.getfeatures = getfeatures


    def increaseFeatureCategoryCount(self, feature, category):

        self.featureCount.setdefault(feature, {})
        self.featureCount[feature].setdefault(category, 0)
        self.featureCount[feature][category] += 1


    def increaseCategoryCount(self, category):

        self.categoryCount.setdefault(category, 0)
        self.categoryCount[category] += 1


    def countTimesFeatureInCategory(self, feature, category):

        if feature in self.featureCount and category in self.featureCount[feature]:
            return float(self.featureCount[feature][category])

        return 0.0


    def countNumberOfItemInCategory(self, category):

        if category in self.categoryCount:
            return float(self.categoryCount[category])

        return 0.0


    def totalNumberOfItemsInCategory(self):

        return sum(self.categoryCount.values())

    def listAllCategories(self):

        return self.categoryCount.keys()

    def train(self, item, category):

        features = self.getfeatures(item)

        for f in features:
            self.increaseFeatureCategoryCount(f, category)

        self.increaseCategoryCount(category)


    def featureProbability(self, feature, category):

        if self.countNumberOfItemInCategory(category) == 0:
            return 0

        return self.countTimesFeatureInCategory(feature, category) / self.countNumberOfItemInCategory(category)

    def weightedprob(self,feature,category,prf,weight=1.0,ap=0.5):
        # Calculate current probability
        basicprob=prf(feature,category)

        # Count the number of times this feature has appeared in
        # all categories
        totals=sum([self.countTimesFeatureInCategory(feature,category) for c in self.listAllCategories(  )])

        # Calculate the weighted average
        bp=((weight*ap)+(totals*basicprob))/(weight+totals)
        return bp












