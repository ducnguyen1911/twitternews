import re
import math


def getWords(doc):
    splitter = re.compile('\\W*')
    # Split the words by non-alpha characters
    words = [s.lower() for s in splitter.split(doc)
             if len(s) > 2 and len(s) < 20]

    # Return the unique set of words only
    return dict([(w, 1) for w in words])


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












