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
import sitemapbuilder


class SiteMapIndexHandler(webapp2.RequestHandler):
    def get(self):

        userAgent = self.request.headers.get('User-Agent', None)

        # Long expiry - so don't need to generate unless an upload has taken place
        expiry_seconds = 60 * 60 * 24 * 7

        if utils.is_cron_task(self.request.headers):
            sitemapbuilder.build_sitemap_index('https://www.markridgwell.co.uk', expiry_seconds)
            sitemapbuilder.build_sitemap_index('http://www.markridgwell.co.uk', expiry_seconds)
            sitemapbuilder.build_sitemap_index('https://www.markridgwell.com', expiry_seconds)
            sitemapbuilder.build_sitemap_index('http://www.markridgwell.com', expiry_seconds)
        else:

            output = sitemapbuilder.build_sitemap_index(self.request.host_url, expiry_seconds)

            utils.add_response_headers(self.request, self.response.headers)
            self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
            self.response.headers['Pragma'] = 'public'
            self.response.headers['Content-Type'] = 'text/xml'
            self.response.out.write(output)


class SiteMapSectionHandler(webapp2.RequestHandler):
    def get(self):

        userAgent = self.request.headers.get('User-Agent', None)

        # Long expiry - so don't need to generate unless an upload has taken place
        expiry_seconds = 60 * 60 * 24 * 7

        if utils.is_cron_task(self.request.headers):
            sitemapbuilder.build_sitemap_section('https://www.markridgwell.co.uk', key, expiry_seconds)
            sitemapbuilder.build_sitemap_section('http://www.markridgwell.co.uk', key, expiry_seconds)
            sitemapbuilder.build_sitemap_section('https://www.markridgwell.com', key, expiry_seconds)
            sitemapbuilder.build_sitemap_section('http://www.markridgwell.com', key, expiry_seconds)
        else:

            output = sitemapbuilder.build_sitemap_section(self.request.host_url, key, expiry_seconds)

            utils.add_response_headers(self.request, self.response.headers)
            self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
            self.response.headers['Pragma'] = 'public'
            self.response.headers['Content-Type'] = 'text/xml'
            self.response.out.write(output)


app = webapp2.WSGIApplication([
    ('/sitemap/[a-zA-Z0-9]', SiteMapSectionHandler),
    ('/sitemap', SiteMapIndexHandler)
])
