from model import *
from util import *
import os
import urllib
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images
from datetime import *
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
        qry = Resource.query(Resource.resource_name == self.request.get('resname')).get()
        if not user or not self.request.get('resname') or qry:
            if not user:
                error = 'Please login first :)'
            elif qry:
                error = 'Resource already exist :)'
            else:
                error = 'Please give a resource name :)'
            template_values = {
                'error_message': error,
                'url': '/addresource',
                'url_linktext': 'try agian!'
            }
            template = JINJA_ENVIRONMENT.get_template('erro.html')
            self.response.write(template.render(template_values))
            return
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
        resource.tags = self.request.get('tags').split(',')
        img=self.request.get('img')
        if img:
            img=images.resize(img,180,180)
            resource.img=img
        if self.request.get('description'):
            resource.description=self.request.get('description')
        resource.description=self.request.get('description')
        if (user and resource.resource_name != ''):
            resource.put()
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
        resource = Resource.query(Resource.resource_name == self.request.get('resource_name')).get()
        start = self.request.get('stime').split(",")
        end = start[:]
        if self.request.get('duration'):
            end[3] = int(end[3]) + int(self.request.get('duration'))
        if not user or not self.request.get('duration') or not checkResourceTime(start, end,
                                                                                 resource.available_time_start,
                                                                                 resource.available_time_end):
            if not user:
                error = 'Please login first!'
            else:
                error = 'Please type in a legal time range :)'
            template_values = {
                'error_message': error,
                'url': '/addreservation?resource_name=' + self.request.get('resource_name'),
                'url_linktext': 'try again'
            }
            template = JINJA_ENVIRONMENT.get_template('erro.html')
            self.response.write(template.render(template_values))
            return
        if not checkReservationConflict(self.request.get('resource_name'),getDatetime(start), getDatetime(end)):
            template_values = {
                'error_message': 'There is another reservation in the time range.\nPlease try another time :)',
                'url': '/addreservation?resource_name=' + self.request.get('resource_name'),
                'url_linktext': 'try again'
            }
            template = JINJA_ENVIRONMENT.get_template('erro.html')
            self.response.write(template.render(template_values))
            return
        reservation = Reservation()
        reservation.resource_name = self.request.get('resource_name')
        reservation.user = user.email()
        reservation.start_datetime = getDatetime(start)
        reservation.start_datetime_string = reservation.start_datetime.strftime("%m/%d/%y,%H:%M")
        reservation.end_datetime = getDatetime(end)
        reservation.end_datetime_string = reservation.end_datetime.strftime("%m/%d/%y,%H:%M:")
        resource = Resource.query(Resource.resource_name == self.request.get('resource_name')).get()
        resource.last_reserve_time = datetime.now()
        resource.reserve_times+=1
        resource.put()
        key=reservation.put()
        send_reserve_confirmation(user.email(),key.get())
        self.redirect('/')


class DeleteReservation(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        reservation = Reservation.query(ndb.AND(Reservation.resource_name == self.request.get('resource_name'),
                                                Reservation.start_datetime_string == self.request.get(
                                                    'start_datetime_string'))).get()
        try:
            if reservation.user == user.email(): # make sure current user is the owner
                reservation.key.delete()
                self.redirect('/')
            else:
                template_values = {
                    'error_message': 'This is not your reservation.',
                    'url': '/',
                    'url_linktext': 'go to landing page'
                }
                template = JINJA_ENVIRONMENT.get_template('erro.html')
                self.response.write(template.render(template_values))
        except:
            template_values = {
                'error_message': 'This reservation is already deleted :)',
                'url': '/',
                'url_linktext': 'go to landing page'
            }
            template = JINJA_ENVIRONMENT.get_template('erro.html')
            self.response.write(template.render(template_values))


class ResourcePage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        resource = Resource.query(Resource.resource_name == self.request.get('resource_name')).get()
        reservations = Reservation.query(Reservation.resource_name == resource.resource_name)
        if user:
            email = user.email()
        else:
            email = ''
        template_values = {
            'resource': resource,
            'reservations': reservations,
            'user': email
        }
        template = JINJA_ENVIRONMENT.get_template('resource.html')
        self.response.write(template.render(template_values))


class ChangeResource(webapp2.RequestHandler):
    def post(self):
        resources = Resource.query(Resource.resource_name == self.request.get('resname'))
        for resource in resources:
            resource.resource_name = self.request.get('resname')
            stime = self.request.get('stime').split(':')
            resource.available_time_start = time(int(stime[0]), int(stime[1]), int(stime[2]))
            etime = self.request.get('etime').split(':')
            resource.available_time_end = time(int(etime[0]), int(etime[1]), int(etime[2]))
            resource.tags = self.request.POST.getall('tag')
            resource.put()
        self.redirect('/')

class ReservationPage(webapp2.RequestHandler):
    def get(self):
        reservation = Reservation.query(Reservation.resource_name == self.request.get('resource_name')).get()
        template_values = {
            'reservation': reservation,
        }
        template = JINJA_ENVIRONMENT.get_template('reservation.html')
        self.response.write(template.render(template_values))


class UserPage(webapp2.RequestHandler):
    def get(self):
        user = self.request.get('user')
        resource = Resource.query(Resource.owner == user)
        deleteOutDateReservation()
        reservations = Reservation.query().order(-Reservation.start_datetime)
        resources = Resource.query(Resource.owner == user)
        template_values = {
            'myresources': resources,
            'reservations': reservations,
            'isIndex': False,
            'user':user,
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class TagPage(webapp2.RequestHandler):
    def get(self):
        tag=self.request.get('tag')
        resources=Resource.query(Resource.tags==tag)
        template_values = {
            'resources':resources,
            'tag':tag
        }
        template = JINJA_ENVIRONMENT.get_template('tag.html')
        self.response.write(template.render(template_values))

class RSSPage(webapp2.RequestHandler):
    def get(self):
        resource_name=self.request.get('resource_name')
        reservations=Reservation.query(Reservation.resource_name==resource_name)
        dt=datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
        RSS=genRSS(reservations,resource_name,dt)
        self.response.write(RSS)

class SearchPage(webapp2.RequestHandler):
    def get(self):
        resource=Resource.query(Resource.resource_name==self.request.get('resource_name')).get()
        if resource:
            query_params = {'resource_name':self.request.get('resource_name')}
            self.redirect('/?' + urllib.urlencode(query_params))
        else:
            template_values = {
                'error_message': 'This resource dosn\'t exsit :)',
                'url': '/',
                'url_linktext': 'go to landing page'
            }
            template = JINJA_ENVIRONMENT.get_template('erro.html')
            self.response.write(template.render(template_values))

class Image(webapp2.RequestHandler):
    def get(self):
        key = ndb.Key(urlsafe=self.request.get('img_id'))
        resource = key.get()
        if resource.img:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(resource.img)
        else:
            self.response.out.write('No image')

class CheckReservation(webapp2.RequestHandler):
    def get(self):
        checkReservation()
        self.redirect('/')

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        resources = Resource.query().order(-Resource.last_reserve_time)
        deleteOutDateReservation()
        reservations = []
        myresources = []
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            myresources = Resource.query(Resource.owner == user.email())
            reservations = Reservation.query(Reservation.user == user.email()).order(Reservation.start_datetime)
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        template_values = {
            'user': user,
            'resources': resources,
            'reservations': reservations,
            'myresources': myresources,
            'url': url,
            'url_linktext': url_linktext,
            'isIndex': True,
            'dt':datetime.now().strftime("%m/%d/%y,%H:%M:%S"),
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/addresource', AddResource),
    ('/addresource/result', AddResResult),
    ('/addreservation', AddReservation),
    ('/addreservation/result', AddReservResult),
    ('/deletereservation', DeleteReservation),
    ('/resource', ResourcePage),
    ('/resource/change', ChangeResource),
    ('/reservation', ReservationPage),
    ('/user', UserPage),
    ('/tag',TagPage),
    ('/RSS',RSSPage),
    ('/search',SearchPage),
    ('/img',Image),
    ('/checkreservation',CheckReservation),
], debug=True)
