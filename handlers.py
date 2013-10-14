import datetime
import webapp2
import json
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
    template_vals = { 'path': self.request.path.lower(), 'users' : users }
    self.response.out.write(utils.render_template("index.html", template_vals))

class ResizeImageHandler(webapp2.RequestHandler):
    def get(self):
        template_vals = { 'path': self.request.path.lower()[ 6 :], 'users' : users }
        self.response.out.write(utils.render_template("index.html", template_vals))

class ThumbnailImageHandler(webapp2.RequestHandler):
    def get(self):
        template_vals = { 'path': self.request.path.lower()[ 10 : -13 ], 'users' : users }
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
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/', ResizeImageHandler),
    ('/image/[\w\-]*/', ResizeImageHandler),
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