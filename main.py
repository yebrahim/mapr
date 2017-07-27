import jinja2
import os
import json
import webapp2
import random
import logging
from google.appengine.api import users
from google.appengine.ext import ndb


class Birthplace(ndb.Model):
    lat = ndb.StringProperty()
    lng = ndb.StringProperty()
    name = ndb.StringProperty()
    birthdate = ndb.DateProperty()


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class IndexPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        template = jinja_environment.get_template('templates/index.html')
        if user:
            self.redirect('/mapr')
            return
        else:
            html = template.render({'signinout': users.create_login_url('/')})
        self.response.out.write(html)


class MaprPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        template = jinja_environment.get_template('templates/mapr.html')
        html = template.render({'signinout': users.create_logout_url('/'),
                                'greeting': user.nickname()})
        self.response.out.write(html)


class MaprAllPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        template = jinja_environment.get_template('templates/places.html')
        html = template.render({'signinout': users.create_logout_url('/'),
                                'greeting': user.nickname()})
        self.response.out.write(html)


class LocationHandler(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            location = self.request.get('location')
            logging.info('got location: ' + location)
            location = json.loads(location)
            lat = str(location['lat'])
            lng = str(location['lng'])
            k = Birthplace.query(Birthplace.name==user.nickname()).get()
            if k:
                instance = k
                instance.lat = lat
                instance.lng = lng
            else:
                instance = Birthplace(name=user.nickname(), lat=lat, lng=lng)
            instance.put()

    def get(self):
        q = Birthplace.query()
        l = q.fetch()
        result = [i.to_dict() for i in l]
        self.response.out.write(json.dumps(result))


app = webapp2.WSGIApplication([
    ('/', IndexPage),
    ('/mapr', MaprPage),
    ('/mapr-all', MaprAllPage),
    ('/postlocation', LocationHandler),
    ('/getlocations', LocationHandler),
], debug=True)
