import datetime
import webapp2

from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext import blobstore


class BlogPost(db.Model):
    title = db.StringProperty(required=True, indexed=False)
    slug = db.StringProperty(required=True)
    body = db.TextProperty()
    tags = db.StringProperty()
    published = db.DateTimeProperty()
    updated = db.DateTimeProperty(auto_now=True)

class ActivityMonth(db.Model):
    date = db.DateProperty(required=True, auto_now_add=True)
    name = db.StringProperty(required=True)
    count = db.IntegerProperty(required=True, default=0)
  
class ActivityCount(db.Model):
    date = db.DateProperty(required=True, auto_now_add=True)
    name = db.StringProperty(required=True)
    count = db.IntegerProperty(required=True, default=0)

class Sponsor(db.Model):
    email = db.EmailProperty(required=True)
    name = db.StringProperty(required=True)
    amount = db.FloatProperty(default=0.0)
    currency = db.StringProperty(default='USD')
    product = db.StringProperty(default='diff')
    quantity = db.IntegerProperty(default=0)
    verifications = db.IntegerProperty(default=0)
    created = db.DateTimeProperty()
    modified = db.DateTimeProperty(auto_now_add=True)

class Report(db.Model):
    name = db.StringProperty()
    subject = db.StringProperty()
    email = db.EmailProperty()
    os = db.StringProperty()
    version = db.StringProperty()
    build = db.StringProperty()
    lastfile = db.StringProperty()
    message = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    blob = blobstore.BlobReferenceProperty()