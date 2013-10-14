import datetime
import webapp2
import json
import hashlib
from collections import defaultdict 

from google.appengine.api import mail
from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.ext import db

import models
import utils

class IndexHandler(webapp2.RequestHandler):
    def get(self):

        searchPath = self.request.path.lower()

        hash = hashlib.sha512(searchPath).hexdigest()

        template_vals = { 'path': searchPath, 'hash' : hash, 'users' : users }
        self.response.out.write(utils.render_template("index.html", template_vals))

class ResizeImageHandler(webapp2.RequestHandler):
    def get(self):

        pos = self.request.path.rfind('/') + 1
        searchPath = self.request.path.lower()[ 6 : pos ]
        width = self.request.path[ pos : -10 ]

        hash = hashlib.sha512(searchPath).hexdigest()

        template_vals = { 'path': searchPath + ':' + width, 'hash' : hash, 'users' : users }
        self.response.out.write(utils.render_template("index.html", template_vals))

class ThumbnailImageHandler(webapp2.RequestHandler):
    def get(self):
        searchPath = self.request.path.lower()[ 10 : -13 ]

        hash = hashlib.sha512(searchPath).hexdigest()

        template_vals = { 'path': searchPath, 'hash' : hash, 'users' : users }
        self.response.out.write(utils.render_template("index.html", template_vals))

app = webapp2.WSGIApplication([
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/', IndexHandler),
    ('/', IndexHandler),
])