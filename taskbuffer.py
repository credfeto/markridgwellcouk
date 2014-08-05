import webapp2

from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
from google.appengine.api import mail

import models
import utils
import sys

class TaskBufferHandler(webapp2.RequestHandler):
    def get(self):

        utils.add_response_headers( self.request, self.response.headers )
        self.response.headers['Content-Type'] = "text/plain"
        
        itemsToPublish = models.PublishableItem.query().fetch(1)
        if itemsToPublish <> None:
            for itemToPublish in itemsToPublish:
                
                self.response.out.write("Id: " + itemToPublish.id +"\r\n" )

                publish = models.GalleryItem.query(models.GalleryItem.id == itemToPublish.id ).get()
                if publish <> None:

                    # publish the item
                    url = 'http://www.markridgwell.co.uk' + publish.path + '?utm_source=mtr&utm_medium=buffer&utm_campaign=publish'
                    user_address = 'buffer-62c71f8f12deed183390@to.bufferapp.com';                    
                    sender_address = "Mark Ridgwell's Photos <bufferpublisher@markridgwellcouk.appspotmail.com>"
                    subject = publish.title + " #photo"
                    body = "@profiles mark ridgwell's photos credfeto @url " + url

                    mail.send_mail(sender_address, user_address, subject, body)
                    
                    #Remove the item we just published so it doesn't go again
                    itemToPublish.key.delete()
                    break

        self.response.out.write("OK")

app = webapp2.WSGIApplication([
    ('/tasks/buffer', TaskBufferHandler)
])
