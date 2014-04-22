__author__ = 'duc07'

import couchdb
from crawler import settings


def couchdb_pager(db, view_name='_all_docs',
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


def count_tweets_per_day(_db_name):
    server = couchdb.Server()
    db = server[_db_name]

    results = {}
    for doc in couchdb_pager(db, bulk=1000):
        if db[doc].startswith('_design/duc'):
            continue
        tweet = db[doc]['text']
        key_date = tweet[:10]
        if key_date not in results:
            results[key_date] = 1
        else:
            results[key_date] += 1
    return results


# -124.626080 is the west most longitude
# -62.361014 is a east most longitude
# +48.987386 is the northern most latitude
# +18.005611 is the southern most latitude
#
# Use "coordinates"."coordinates":
# Long first, then Lat
def is_in_US(log, lat):
    if log in range(-124.626080, -62.361014) and lat in range(18.005611, 48.987386):
        return True
    else:
        return False


def filter_for_US_tweets(_db_name):
    server = couchdb.Server()
    db = server[_db_name]
    db_US = server[settings.database_us]

    results = {}
    for doc in couchdb_pager(db, bulk=1000):
        tweet = db[doc]['text']
        latlog = db[doc]['coordinates']['coordinates']
        lat = latlog[0]
        log = latlog[1]
        if is_in_US(log, lat):
            db_US["tweet:%d" % tweet['id']] = tweet
    return results



def main():
    counter = count_tweets_per_day(settings.database_geo)
    for date, numb in counter.iteritems():
        print 'date ', date, ' - numb tweets: ', numb

if __name__ == "__main__":
    main()

# Code for view counchDb
# function(doc) {
#   emit(parseTwitterDate(doc.created_at), doc);
# }
#
# function parseTwitterDate(text) {
# return new Date(Date.parse(text.replace(/( +)/, ' UTC$1')));
# }