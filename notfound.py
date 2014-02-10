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


class NotFoundHandler(webapp2.RequestHandler):
    def get(self):

        template_vals = { 'path': searchPath, 'track': track, 'hash' : hash, 'users' : users }
        self.response.out.write(utils.render_template("notfound.html", template_vals))
        self.response.set_status(404) 

app = webapp2.WSGIApplication([
  ('/.*', NotFoundHandler),    
])