import datetime
import webapp2

from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.ext import blobstore

#overview
# https://developers.google.com/appengine/docs/python/ndb/

# structured proerties
# https://developers.google.com/appengine/docs/python/ndb/properties#structured

# Queries
# https://developers.google.com/appengine/docs/python/ndb/queries

class GeneratedItem(ndb.Model):
    id = ndb.StringProperty(required=True)
    text = ndb.TextProperty(required=True)
    updated = ndb.DateTimeProperty(required=True,auto_now=True)

class PublishableItem(ndb.Model):
    id = ndb.StringProperty(required=True)
    updated = ndb.DateTimeProperty(required=True,auto_now=True)
        
class ItemViewCount(ndb.Model):
    id = ndb.StringProperty(required=True)
    path = ndb.StringProperty(required=True)
    viewCount = ndb.IntegerProperty(required=True,default=0)
    shareCount = ndb.IntegerProperty(required=True,default=0)
    updated = ndb.DateTimeProperty(required=True,auto_now=True)

class UserPrefs(db.Model):
    userid = db.StringProperty()
    lastEmailAddress = db.EmailProperty()
    lastNickname = db.StringProperty()
    banned = db.BooleanProperty()
    firstLoggedIn = db.DateTimeProperty()
    lastAccessed = db.DateTimeProperty()

class ResizedImage(ndb.Model):
    width = ndb.IntegerProperty(required=True)
    height = ndb.IntegerProperty(required=True)

class BreadcrumbItem(ndb.Model):
    id = ndb.StringProperty(required=True)
    path = ndb.StringProperty(required=True)
    title = ndb.TextProperty(required=True)
    description = ndb.TextProperty(required=True)


class ChildItem(ndb.Model):
    id = ndb.StringProperty(required=True)
    path = ndb.StringProperty(required=True)
    title = ndb.TextProperty(required=True)
    type = ndb.StringProperty(required=True)
    description = ndb.TextProperty(required=True)
    thumbnail = ndb.StructuredProperty(ResizedImage, repeated=False, required=False)

class MetadataProperty(ndb.Model):
    name = ndb.StringProperty(required=True)
    value = ndb.StringProperty(required=True)

class GalleryItem(ndb.Model):
    id = ndb.StringProperty(required=True)
    path = ndb.StringProperty(required=True)
    indexSection = ndb.StringProperty(required=False)
    title = ndb.TextProperty(required=True)
    type = ndb.StringProperty(required=True)
    description = ndb.TextProperty(required=True)
    rating = ndb.IntegerProperty(required=False)
    location = ndb.GeoPtProperty(required=False)
    breadcrumbs = ndb.StructuredProperty(BreadcrumbItem, repeated=True, required=False)
    children = ndb.StructuredProperty(ChildItem, repeated=True, required=False)
    resizes = ndb.StructuredProperty(ResizedImage, repeated=True, required=False)
    metadata = ndb.StructuredProperty(MetadataProperty, repeated=True, required=False)
    keywords = ndb.StringProperty(repeated=True, required=False)
    firstSibling = ndb.StructuredProperty(ChildItem, repeated=False, required=False)
    previousSibling = ndb.StructuredProperty(ChildItem, repeated=False, required=False)
    nextSibling = ndb.StructuredProperty(ChildItem, repeated=False, required=False)
    lastSibling = ndb.StructuredProperty(ChildItem, repeated=False, required=False)
    updated = ndb.DateTimeProperty(auto_now=True)
