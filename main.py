from model import *
from util import *
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class AddResource(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        template_values = {
            'url': url,
            'url_linktext': url_linktext,
        }
        template = JINJA_ENVIRONMENT.get_template('add_resource.html')
        self.response.write(template.render(template_values))

class addResResult(webapp2.RequestHandler):

    def post(self):
        user = users.get_current_user()
        resource=Resource()
        resource.owner=user.email()
        resource.resource_name=self.request.get('resname')
        try:
            start=self.request.get('stime').split(",")
            end=self.request.get('etime').split(",")
            resource.available_time_start=getTime(start[0],start[1])
            resource.available_time_end=getTime(end[0],end[1])
        except:
            self.response.write('error')
            return
        resource.tags=tags=self.request.get('tags').split(',')
        if (user and resource.resource_name!=''):
            key=resource.put()
            self.redirect('/')
        else:
            self.response.write('error')

class addReservation(webapp2.RequestHandler):

    def get(self):
        resource_name=self.request.get('resource_name')
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        template_values = {
            'resource_name':resource_name,
            'url': url,
            'url_linktext': url_linktext,
        }
        template = JINJA_ENVIRONMENT.get_template('add_reservation.html')
        self.response.write(template.render(template_values))

class addReservResult(webapp2.RequestHandler):

    def post(self):
        user = users.get_current_user()
        reservation=Reservation()
        reservation.user=user.email()
        reservation.resource_name=self.request.get('resname')
        start=self.request.get('stime').split(",")
        reservation.start_datetime=getDatetime(start)
        reservation.duration=int(self.request.get('duration'))
        key=reservation.put()
        self.redirect('/')

class MainHandler(webapp2.RequestHandler):

    def get(self):
        resources= Resource.query()
        reservations=Reservation.query()
        template = JINJA_ENVIRONMENT.get_template('index.html')
        template_values = {
            'resources': resources,
            'reservations':reservations
        }
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/addresource', AddResource),
    ('/addresource/result', addResResult),
    ('/addreservation', addReservation),
    ('/addreservation/result', addReservResult),
], debug=True)
