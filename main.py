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


class AddResResult(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        resource = Resource()
        resource.owner = user.email()
        resource.resource_name = self.request.get('resname')
        try:
            start = self.request.get('stime').split(",")
            end = self.request.get('etime').split(",")
            resource.available_time_start = getTime(start[0], start[1])
            resource.available_time_end = getTime(end[0], end[1])
        except:
            self.response.write('error')
            return
        resource.tags = tags = self.request.get('tags').split(',')
        if (user and resource.resource_name != ''):
            key = resource.put()
            self.redirect('/')
        else:
            self.response.write('error')


class AddReservation(webapp2.RequestHandler):
    def get(self):
        resource_name = self.request.get('resource_name')
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        template_values = {
            'resource_name': resource_name,
            'url': url,
            'url_linktext': url_linktext,
        }
        template = JINJA_ENVIRONMENT.get_template('add_reservation.html')
        self.response.write(template.render(template_values))


class AddReservResult(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        reservation = Reservation()
        reservation.user = user.email()
        reservation.resource_name = self.request.get('resname')
        start = self.request.get('stime').split(",")
        reservation.start_datetime = getDatetime(start)
        reservation.duration = int(self.request.get('duration'))
        key = reservation.put()
        self.redirect('/')


class ResourcePage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        resources = Resource.query(Resource.resource_name == self.request.get('resource_name'))
        template_values = {
            'resources': resources,
            'user': user.email()
        }
        template = JINJA_ENVIRONMENT.get_template('resource.html')
        self.response.write(template.render(template_values))

class ChangeResource(webapp2.RequestHandler):

    def post(self):
        resources = Resource.query(Resource.resource_name==self.request.get('resname'))
        for resource in resources:
            resource.resource_name=self.request.get('resname')
            stime=self.request.get('stime').split(':')
            resource.available_time_start=time(int(stime[0]),int(stime[1]),int(stime[2]))
            etime=self.request.get('etime').split(':')
            resource.available_time_end=time(int(etime[0]),int(etime[1]),int(etime[2]))
            resource.tags=[self.request.get('tags')]
            resource.put()
        self.redirect('/')

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        resources = Resource.query()
        reservations = Reservation.query()
        myresources = Resource.query(Resource.owner == user.email())
        template = JINJA_ENVIRONMENT.get_template('index.html')
        template_values = {
            'resources': resources,
            'reservations': reservations,
            'myresources': myresources
        }
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/addresource', AddResource),
    ('/addresource/result', AddResResult),
    ('/addreservation', AddReservation),
    ('/addreservation/result', AddReservResult),
    ('/resource', ResourcePage),
    ('/resource/change', ChangeResource)
], debug=True)
