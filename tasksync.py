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
import pubsubhubub

class TaskSyncHandler(webapp2.RequestHandler):
    def get(self):

        utils.add_response_headers( self.request, self.response.headers )
        self.response.headers['Content-Type'] = "text/plain"
        self.response.out.write("OK")

    def post(self):
        content = self.request.body
                
        itemsWritten = sync.synchronize_common(content)

        utils.add_response_headers( self.request, self.response.headers )
        self.response.headers['Content-Type'] = "text/plain"
        self.response.out.write("Items Written: " + str(itemsWritten))

class TaskPublishHandler(webapp2.RequestHandler):
    def get(self):

        pubsubhubub.update( 'http://markridgwell.superfeedr.com', 'http://www.markridgwell.co.uk/rss.xml')

        utils.add_response_headers( self.request, self.response.headers )
        self.response.headers['Content-Type'] = "text/plain"
        self.response.out.write("OK")

app = webapp2.WSGIApplication([
    ('/tasks/publish', TaskPublishHandler),
    ('/tasks/sync', TaskSyncHandler)
])
