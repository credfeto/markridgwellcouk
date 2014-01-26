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
from google.appengine.api import memcache

import models
import utils
import sync
import sys

class RssHandler(webapp2.RequestHandler):
    def get(self):

        ##need to implement this!
        count = 30

        try:
            recentItems = memcache.get('rss')
        except KeyError:
            recentItems = models.GalleryItem.query(models.GalleryItem.type == 'photo').order('-updated').fetch(count)
        memcache.set('rss', recentItems)

        self.response.headers['Cache-Control'] = 'public,max-age=%s' % 86400
        self.response.headers['Content-Type'] = 'application/rss+xml'

        when = datetime.datetime.now()
        if recentItems:
            latestDate = None
            for item in recentItems:
                if latestDate is None:
                    latestDate = item.updated
                else:
                    if latestDate < item.updated:
                        latestDate = item.updated
            if latestDate <> None:
                when = latestDate

        template_vals = {'items' : recentItems, 'pubdate' : when }
        self.response.out.write(utils.render_template("rss.html", template_vals))
        #self.response.set_status(404) 

app = webapp2.WSGIApplication([
    ('/rss\.xml', RssHandler)
])
