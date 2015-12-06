from google.appengine.ext import ndb

class Resource(ndb.Model):
    owner = ndb.StringProperty(required=True)
    resource_name = ndb.StringProperty(required=True)
    available_time_start = ndb.TimeProperty(indexed=False)
    available_time_end = ndb.TimeProperty(indexed=False)
    tags = ndb.StringProperty(repeated=True)

class Reservation(ndb.Model):
    user = ndb.StringProperty(required=True)
    resource_name = ndb.StringProperty(required=True)
    start_datetime = ndb.DateTimeProperty(required=True)
    duration = ndb.IntegerProperty(required=True)