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


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class IndexPage(webapp2.RequestHandler):
    """Only used if the user is signed out"""
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
    """Page takes the user's birthplace on the map, sends it to backend"""
    def get(self):
        user = users.get_current_user()

        template = jinja_environment.get_template('templates/mapr.html')
        html = template.render({'signinout': users.create_logout_url('/'),
                                'greeting': user.nickname()})
        self.response.out.write(html)


class MaprAllPage(webapp2.RequestHandler):
    """Page shows the all the birthplace entries in the database, shown on the map"""
    def get(self):
        user = users.get_current_user()

        template = jinja_environment.get_template('templates/places.html')
        html = template.render({'signinout': users.create_logout_url('/'),
                                'greeting': user.nickname()})
        self.response.out.write(html)


class LocationHandler(webapp2.RequestHandler):
    def post(self):
        """POST request handler, saves the new location into the database.
        A user can only have one row in the database, so multiple entries
        will overwrite each other."""
        user = users.get_current_user()
        # Make sure the user is signed in, because we need their identity
        # to save it along with the coordinates
        if user:
            # Get the request data
            location = self.request.get('location')
            location = json.loads(location)
            lat = str(location['lat'])
            lng = str(location['lng'])
            k = Birthplace.query(Birthplace.name==user.nickname()).get()
            # Let's first check if this user already exists in the database
            # If they do, get that entry (its key) and modify it
            if k:
                instance = k
                instance.lat = lat
                instance.lng = lng
            else:
                instance = Birthplace(name=user.nickname(), lat=lat, lng=lng)
            instance.put()

    def get(self):
        """GET request returns all location entries in the database."""
        q = Birthplace.query()
        l = q.fetch()
        # Turn the list from a list of Birthplace objects into list of dicts
        result = [i.to_dict() for i in l]
        self.response.out.write(json.dumps(result))


app = webapp2.WSGIApplication([
    ('/', IndexPage),
    ('/mapr', MaprPage),
    ('/mapr-all', MaprAllPage),
    ('/postlocation', LocationHandler),
    ('/getlocations', LocationHandler),
], debug=True)
