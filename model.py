from google.appengine.ext import ndb
from datetime import datetime

class Resource(ndb.Model):
    owner = ndb.StringProperty(required=True)
    resource_name = ndb.StringProperty(required=True)
    available_time_start = ndb.TimeProperty(indexed=False)
    available_time_end = ndb.TimeProperty(indexed=False)
    tags = ndb.StringProperty(repeated=True)
    last_reserve_time=ndb.DateTimeProperty(required=True,default=datetime(2000,1,1,1,0))

class Reservation(ndb.Model):
    user = ndb.StringProperty(required=True)
    resource_name = ndb.StringProperty(required=True)
    start_datetime = ndb.DateTimeProperty(required=True)
    end_datetime = ndb.DateTimeProperty(required=True)