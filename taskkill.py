import webapp2

from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
from google.appengine.api import mail

import models
import utils
import sys

class TaskKillHandler(webapp2.RequestHandler):
    def get(self):

        self.response.headers['Content-Type'] = "text/plain"

        id = 'cff7bc268029dbf1205927eba4a173aa03797cac03c48409f481be049a8803bef9dab95612cc406d719a25c1ab98fa285fc54199f491da127f5c17f26daa5ac2'
        
        publish = models.PublishableItem.query(models.PublishableItem.id == id ).get()
        if publish <> None:

            
            #Remove the item 
            publish.key.delete()
            break

        self.response.out.write("OK")

app = webapp2.WSGIApplication([
    ('/tasks/kill', TaskKillHandler)
])
