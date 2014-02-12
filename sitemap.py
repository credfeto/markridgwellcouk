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

        expiry_seconds = 60 * 60 * 12
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

            print 'here1'

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


class SiteMapYearHandler(webapp2.RequestHandler):
    def get(self):

        ##need to implement this!

        self.response.set_status(404) 


app = webapp2.WSGIApplication([
    ('/sitemap/[0-9]+', SiteMapYearHandler),
    ('/sitemap', SiteMapIndexHandler)
])
