import datetime
import webapp2
import json
import hashlib
import urllib2
from collections import defaultdict 

from google.appengine.api import mail
from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import urlfetch 

import models
import utils
import sync
import sys

class SiteMapIndexHandler(webapp2.RequestHandler):
    def get(self):

        ##need to implement this!

        self.response.set_status(404) 

class SiteMapYearHandler(webapp2.RequestHandler):
    def get(self):

        ##need to implement this!

        self.response.set_status(404) 


app = webapp2.WSGIApplication([
    ('/sitemap/[0-9]+', SiteMapYearHandler)
    ('/sitemap', SiteMapIndexHandler)
])
