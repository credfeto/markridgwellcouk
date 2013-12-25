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
from google.appengine.ext import db
from google.appengine.api import urlfetch 

import models
import utils

class TaskSyncHandler(webapp2.RequestHandler):
    def get(self):
        
        
        url = 'https://markridgwell-data.s3.amazonaws.com/site.js'
        self.response.write('<br/>Downloading from: ' + url );

        result = urlfetch.fetch(url);
        if result.status_code == 200:
            self.response.write(result.content+ '<br/>')

            decoded = json.loads(result.content)
            version = decoded["version"]

            self.response.write('<br/>' + "Decoded Version: " + str(version) )

            for item in decoded["items"]:
                path = item["Path"]
                title = item["Title"]
                type = "virtual"
                description = item["Description"]
                rating = item["Rating"]
                location = None

                #description = item["description"]

                hash = utils.generate_url_hash(path)
                self.response.write('<br/>' + "Path: " + path )
                self.response.write('<br/>' + "Hash: " + hash )

                q = models.GalleryItem.query(models.GalleryItem.id == hash)

                dbItem = q.get()
                if dbItem is None:
                    dbItem = models.GalleryItem(
                                                id = hash,
                                                path = path,
                                                title = title,
                                                type = type,
                                                description = description,
                                                rating = rating,
                                                location = location
                                                )
                    dbItem.put()
                    self.response.write('<br/>Created')
                else:
                    dbItem.path = path
                    dbItem.title = title
                    dbItem.type = type
                    dbItem.description = description
                    dbItem.rating = rating
                    dbItem.location = location
                    
                    dbItem.put()

                    self.response.write('<br/>Updated')

                self.response.write('<br/>')
        else:
            self.response.write("Error!")

app = webapp2.WSGIApplication([
    ('/tasks/sync', TaskSyncHandler)
], debug=True)
