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
from google.appengine.api import capabilities
from google.appengine.api import memcache


import models
import utils
import sync
import sys

class SiteMapIndexHandler(webapp2.RequestHandler):
    def get(self):

        # Long expiry - so don't need to generate unless an upload has taken place
        expiry_seconds = 60 * 60 * 24 * 7
        memcachedKey = 'sitemap-index-output'
        output = ''
        
        memcacheEnabled = capabilities.CapabilitySet('memcache').is_enabled()

        if memcacheEnabled:
            try:
                output = memcache.get(memcachedKey)
            except KeyError:
                output = ''

        if output is None or len(output) == 0:
            
            when = datetime.datetime.now()

            items = []
            
            items.append( { 'index' : '0', 'lastMod' : when } )
            items.append( { 'index' : '1', 'lastMod' : when } )
            items.append( { 'index' : '2', 'lastMod' : when } )
            items.append( { 'index' : '3', 'lastMod' : when } )
            items.append( { 'index' : '4', 'lastMod' : when } )
            items.append( { 'index' : '5', 'lastMod' : when } )
            items.append( { 'index' : '6', 'lastMod' : when } )
            items.append( { 'index' : '7', 'lastMod' : when } )
            items.append( { 'index' : '8', 'lastMod' : when } )
            items.append( { 'index' : '9', 'lastMod' : when } )
            items.append( { 'index' : 'a', 'lastMod' : when } )
            items.append( { 'index' : 'b', 'lastMod' : when } )
            items.append( { 'index' : 'c', 'lastMod' : when } )
            items.append( { 'index' : 'd', 'lastMod' : when } )
            items.append( { 'index' : 'e', 'lastMod' : when } )
            items.append( { 'index' : 'f', 'lastMod' : when } )

            template_vals = {'indexes' : items, 'host' : self.request.host_url }

            output = utils.render_template("sitemapindex.html", template_vals)
        
            if memcacheEnabled:    
                memcache.set(memcachedKey, output, expiry_seconds)

        self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
        self.response.headers['Pragma'] = 'public'
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(output)


class SiteMapSectionHandler(webapp2.RequestHandler):
    def get(self):

        key = self.request.path[-1:].lower()

        memcacheEnabled = capabilities.CapabilitySet('memcache').is_enabled()

        # Long expiry - so don't need to generate unless an upload has taken place
        expiry_seconds = 60 * 60 * 24 * 7
        memcachedKey = 'sitemap-section-' + key + '-output'
        output = ''

        if memcacheEnabled:
            try:
                output = memcache.get(memcachedKey)
            except KeyError:
                output = ''

        if output is None or len(output) == 0:
            
            q = models.GeneratedItem.query(models.GeneratedItem.id == memcachedKey)
            pregenerated = q.get()
            if pregenerated is None:

                when = datetime.datetime.now()

                q = models.GalleryItem.query(models.GalleryItem.indexSection == key, projection=["path"]).order(models.GalleryItem.path)

                items = []
                for item in q:
                    items.append( { 'path' : item.path } )

                template_vals = {'items' : items, 'host' : self.request.host_url }

                output = utils.render_template("sitemapsection.html", template_vals)
        
                pregenerated = models.GeneratedItem(
                                                            id = memcachedKey,
                                                            text = output,
                                                            updated = when )
                pregenerated.put();
            else:
                output = pregenerated.text

            if memcacheEnabled:    
                memcache.set(memcachedKey, output, expiry_seconds)

        self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
        self.response.headers['Pragma'] = 'public'
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(output)

app = webapp2.WSGIApplication([
    ('/sitemap/[a-zA-Z0-9]', SiteMapSectionHandler),
    ('/sitemap', SiteMapIndexHandler)
])
