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

class TaskSyncHandler(webapp2.RequestHandler):
    def get(self):

        self.response.out.write("OK")

app = webapp2.WSGIApplication([
    ('/tasks/sync', TaskSyncHandler)
], debug=True)
