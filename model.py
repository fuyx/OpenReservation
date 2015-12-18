
from google.appengine.ext import ndb
from datetime import datetime

class Resource(ndb.Model):
    owner = ndb.StringProperty(required=True)
    resource_name = ndb.StringProperty(required=True)
    available_time_start = ndb.TimeProperty(indexed=False)
    available_time_end = ndb.TimeProperty(indexed=False)
    tags = ndb.StringProperty(repeated=True)
    last_reserve_time=ndb.StringProperty(required=True,default="01/01/2000,10:00 to 12:00")
    reserve_times=ndb.IntegerProperty(required=True,default=0)
    img=ndb.BlobProperty()
    description=ndb.TextProperty()

class Reservation(ndb.Model):
    user = ndb.StringProperty(required=True)
    resource_name = ndb.StringProperty(required=True)
    start_datetime = ndb.DateTimeProperty(required=True)
    end_datetime = ndb.DateTimeProperty(required=True)
    start_datetime_string = ndb.StringProperty(required=True)
    end_datetime_string = ndb.StringProperty(required=True)