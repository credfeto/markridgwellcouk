import datetime
import webapp2

from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext import blobstore


class GalleryItem(db.Model):
    id = db.StringProperty(required=True, indexed=True)
    path = db.StringProperty(required=True, indexed=True)
    title = db.StringProperty(required=True, indexed=False)
    type = db.StringProperty(required=True, indexed=False)
    description = db.StringProperty(required=True, indexed=False)
    rating = db.RatingProperty(required=False, indexed=False)
    location = db.GeoPtProperty(required=False, indexed=False)
    updated = db.DateTimeProperty(auto_now=True)
