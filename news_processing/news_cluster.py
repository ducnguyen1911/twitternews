__author__ = 'duc07'


class TweetCluster:
    threshold = 1

    def __init__(self):
        print 'self'

    def calc_lsh(self):
        print 'calculate LSH'

    def get_set_collide(self, _doc):
        print 'return set of colliding documents for a given document using LSH'

    def cluster(self, _clusters, _doc):
        # format: _clusters: {cluster1: [center1, [doc1, doc2, doc3,...]], cluster2: [], cluster3: []}
        # format: _doc: {term1: tfidf1, term2: tfidf2}
        if len(_clusters) == 0:
            # no cluster
            print 'no cluster'
        else:
            min_dist = 10000
            min_cluster = ''
            for name, cluster in _clusters.iteritems():
                centroid = cluster[0]
                if self.distance(centroid, _doc) < min_dist:
                    min_cluster = name
            # assign _doc to cluster with min distance
            _clusters[min_cluster][1].append(_doc)
            self.update_cluster(_clusters[min_cluster])


    def distance(self, _doc1, _doc2):
        return 0

    def update_cluster(self, _cluster):
        return 0

    # when new tweets come -> new vocabularies -> how update tf-idf of old tweets -> just update df of center of cluster
    # since when new tweets come, idf does not change, only df of all tweets change (and df of a term for all docs
    # are same.)

