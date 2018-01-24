import datetime
import pymongo

from pymongo import MongoClient


class MovieDAO:
    """The Movie Data Access Object handles all interactions with the
    myMovies collection.
    """

    def __init__(self, db):
        self.db = db
        self.movies = self.db.myMovies

    def find_any_movie(self):
        movie = self.movies.find_one()
        print('Movie: %s' % (movie))

    def find_by_type(self, type):
        query = {"type": type}
        try:
            cursor = self.movies.find(query)
        except Exception as e:
            print("Error: %s" % (e))
        print('Movies with type "%s":' % (type))
        sanity = 0
        for doc in cursor:
            print(doc)
            sanity += 1
            if (sanity > 10):
                break

    def find_one_by_title(self, title):
        query = {"title": title}
        try:
            doc = self.movies.find_one(query)
        except Exception as e:
            print("Error: %s" % (e))
        print('Movie: %s' % (doc))

    def find_by_period(self, start, end):
        query = {"year": {"$gte" : start, '$lte' : end}}
        try:
            cursor = self.movies.find(query)
        except Exception as e:
            print("Error: %s" % (e))
        print('Video %d-%d:' % (start, end))
        sanity = 0
        for doc in cursor:
            print(doc)
            sanity += 1
            if (sanity > 10):
                break

    def find_by_min_rating_with_projection(self, rating):
        query ={'rating': {'$gte': rating}}
        projection = {'title': 1, 'rating': 1, '_id': 0}
        try:
            cursor = self.movies.find(query, projection)
        except Exception as e:
            print("Error: %s" % (e))
        print('Video with its rating:')
        sanity = 0
        for doc in cursor:
            print(doc)
            sanity += 1
            if (sanity > 10):
                break

    def find_with_reg_expression(self, regex):
        query = {'title': {'$regex': regex, '$options': 'i'}}
        projection = {'title': 1, 'year': 1, 'rating':1, '_id': 0}
        try:
            cursor = self.movies.find(query, projection)
        except Exception as e:
            print("Error: %s" % (e))
        print('Regexpression: %s.\nVideo:' % (regex))
        for doc in cursor:
            print(doc)

    def find_sort_skip_limit(self, sort_by, skip, limit):
        query = {}
        try:
            cursor = self.movies.find(query)
            cursor.sort(sort_by, pymongo.ASCENDING).skip(skip).limit(limit)

            #cursor = self.movies.find(query).skip(skip)
            #cursor.limit(limit)
            #cursor.sort([(sort_by, pymongo.ASCENDING),
            #             ('title', pymongo.DESCENDING)])
        except Exception as e:
            print("Error: %s" % (e))
        print('Videos sorted by %s skipped %d limitted %d' % (sort_by, skip,
                                                              limit))
        for doc in cursor:
            print(doc)

    def insert_one(self, *, title=None, year=None, type_=None, rating=None,
                   country=None, _id=None):
        movie = {}
        if title:
            movie.update({'title': title})
        if year:
            movie.update({'year': year})
        if type_:
            movie.update({'type': type_})
        if rating:
            movie.update({'rating': rating})
        if country:
            movie.update({'country': country})
        if _id:
            movie.update({'_id': _id})

        try:
            self.movies.insert_one(movie)
            del(movie['_id'])
            self.movies.insert_one(movie)
        except Exception as e:
            print("Insert failed: %s" % (e))

        try:
            self.movies.insert_one(movie)
        except Exception as e:
            print("Insert failed: %s" % (e))

    def update_one_by_title(self, *, title=None, year=None, type_=None,
                            rating=None, country=None, _id=None):
        movie = {}
        if year:
            movie.update({'year': year})
        if type_:
            movie.update({'type': type_})
        if rating:
            movie.update({'rating': rating})
        if country:
            movie.update({'country': country})
        if _id:
            movie.update({'_id': _id})

        try:
            old_movie = self.movies.find_one({'title': title})
            print('Old video: %s' % (old_movie))
            # update using set
            record_id = old_movie['_id']
            result = self.movies.update_one({'_id': record_id},
                                            {'$set': movie})
            print('Num matched: %s' % (result.matched_count))
            if _id:
                movie = self.movies.find_one({'_id': _id})
            else:
                movie = self.movies.find_one({'_id': record_id})
            print('New video: %s' % (movie))
        except Exception as e:
            print("Error: %s" % (e))

    def update_many_add_review_date(self, date=None):
        try:
            # update all the docs
            review_date = None
            if not date:
                date = datetime.datetime.utcnow()
            result = self.movies.update_many({},
                                             {'$set': {'review_date': date}})
            print("Num matched: %d" % (result.matched_count))
        except Exception as e:
            print("Error: %s" % (e))

    # removes all review dates
    def remove_all_review_dates(self):
        try:
            result = movies.update_many({'review_date':{'$exists':True}},
                                        {'$unset':{'review_date':1}})
            print("Number od updated docs: %s" % (result.matched_count))
        except Exception as e:
            print("Error: %s" % (e))

    # add a review date to single record using replace_one
    def add_review_date_using_replace_one(self, movie_title):
        try:
            movie = self.movies.find_one({'title': movie_title})
            print('Old video data: %s' % (movie))

            # add a review_date
            movie['review_date'] = datetime.datetime.utcnow()
            # update the record with replace_one
            record_id = movie['_id']

            self.movies.replace_one({'_id': record_id}, movie)
            movie = self.movies.find_one({'_id': record_id})
            print('Video data after replacing: %s' % (movie))
        except Exception as e:
            print("Error: %s" % (e))

    def upsert_data_by_title(self, *, title, key, value):
        try:
            self.movies.update_one({'title': title}, {'$set':{key: value}},
                                   upsert=True)
#            self.movies.update_many({'title':title}, {'$set':{key: value}},
#                                    upsert=True)

            movie = self.movies.find_one({'title': title})
            print('New data: %s' % (movie))
        except Exception as e:
            print("Error: %s" % (e))

    def remove_movie_by_title(self, title):
        try:
            result = self.movies.delete_many({'title': title})
            print("Num removed: %d" % (result.deleted_count))
        except Exception as e:
            print("Error: %s" % (e))

    def get_next_sequence_number(self, title):
        try:
            counter = self.movies.find_one_and_update(filter={'title':title},
                                                 update={'$inc':{'viewed':1}},
                                                 upsert=True,
                                                 return_document=pymongo.\
                                                     ReturnDocument.AFTER)
            counter_value = counter['viewed']
            print('Viewed times: %s' % (counter_value))
        except Exception as e:
            print("Error: %s" % (e))


if __name__ == "__main__":
    #connect to database
    connection = MongoClient('mongodb://localhost')

    db = connection.video
    # handle to names collection
    #print(db.collection_names(include_system_collections=False))

    my_movies = MovieDAO(db)
    my_movies.find_any_movie()
    my_movies.find_by_type('movie')
    my_movies.find_one_by_title('Shrek')
    my_movies.find_by_period(2000, 2009)
    my_movies.find_by_min_rating_with_projection(5)
    my_movies.find_with_reg_expression('Trek|Shrek')
    my_movies.find_sort_skip_limit('year', 4, 1)
    my_movies.insert_one(title='Mavka', year=2018, type_='cartoon',
                         rating=None, country='Ukraine', _id='Mavka')
    my_movies.update_one_by_title(title='Shrek', year=2001, type_='cartoon',
                                  rating=9.8)
    my_movies.update_one_by_title(title='Shrek II', year=2004,
                                  type_='cartoon', rating=9.5, _id='shrek_2')
    my_movies.update_many_add_review_date('2000')
    my_movies.update_many_add_review_date()
    my_movies.remove_all_review_dates()
    my_movies.add_review_date_using_replace_one('Mavka')
    my_movies.upsert_data_by_title(title='Mavka', key='producer',
                                   value='Iryna Kostyuk')
    my_movies.remove_movie_by_title('Mavka')
    my_movies.get_next_sequence_number('Shrek')

