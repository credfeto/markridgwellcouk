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
from google.appengine.api import capabilities

import models
import utils
import sync
import sys


class RssHandler(webapp2.RequestHandler):
    def get(self):

        # Long expiry - so don't need to generate unless an upload has taken place
        expiry_seconds = 60 * 60 * 24 * 7
        memcachedKey = 'rss-output'
        output = ''

        memcacheEnabled = capabilities.CapabilitySet('memcache').is_enabled()

        if memcacheEnabled:
            try:
                output = memcache.get(memcachedKey)
            except KeyError:
                output = ''

        if output is None or len(output) == 0:

            q = models.GeneratedItem.query(models.GeneratedItem.id == memcachedKey)
            pregenerated = q.get()
            if pregenerated is None:
                count = 200

                recentItemsSearch = models.GalleryItem.query(models.GalleryItem.type == 'photo').order(
                    -models.GalleryItem.updated).fetch(count)
                when = datetime.datetime.now()
                builddate = when

                recentItems = []
                if recentItemsSearch:
                    latestDate = None
                    for item in recentItemsSearch:
                        if utils.is_public_publishable_path(item.path):
                            recentItems.append(item)
                            if latestDate is None:
                                latestDate = item.updated
                            else:
                                if latestDate < item.updated:
                                    latestDate = item.updated
                    if latestDate <> None:
                        when = latestDate

                template_vals = {'host': self.request.host_url, 'items': recentItems, 'pubdate': when,
                                 'builddate': builddate}

                output = utils.render_template("rss.html", template_vals)

                pregenerated = models.GeneratedItem(
                    id=memcachedKey,
                    text=output,
                    updated=when)
                pregenerated.put();
            else:
                output = pregenerated.text

        if memcacheEnabled:
            memcache.set(memcachedKey, output, expiry_seconds)

        utils.add_response_headers(self.request, self.response.headers)
        self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
        self.response.headers['Pragma'] = 'public'
        self.response.headers['Content-Type'] = 'application/rss+xml'
        self.response.out.write(output)


class RssRedirectHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect('https://www.markridgwell.co.uk/rss.xml', permanent=True)


app = webapp2.WSGIApplication([
    ('/rss\.xml', RssHandler),
    ('/rss/.*\.xml', RssRedirectHandler),
    ('/RSS/.*\.xml', RssRedirectHandler)
])
