import datetime
import webapp2
import json
from collections import defaultdict 

from google.appengine.api import mail
from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.ext import db

import models
import utils


class ContactHandler(webapp2.RequestHandler):
    def get(self):

        track = utils.should_track( self.request.headers )

        template_vals = { 'track' : track, 'showShare' : False }

        self.response.out.write(utils.render_template("contact.html", template_vals))

app = webapp2.WSGIApplication([
    ('/contact/', ContactHandler),
])