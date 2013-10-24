import datetime
import webapp2

from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.ext import blobstore

#overview
# https://developers.google.com/appengine/docs/python/ndb/

# structured proerties
# https://developers.google.com/appengine/docs/python/ndb/properties#structured

# Queries
# https://developers.google.com/appengine/docs/python/ndb/queries

class ChildItem(ndb.Model):
    id = ndb.StringProperty(required=True, indexed=True)
    path = ndb.StringProperty(required=True, indexed=True)
    title = ndb.StringProperty(required=True, indexed=False)

class ResizedImage(ndb.Model):
    width = ndb.IntegerProperty(required=True)
    height = ndb.IntegerProperty(required=True)

class MetadataProperty(ndb.Model):
    name = ndb.StringProperty(required=True)
    value = ndb.StringProperty(required=True)
     
class GalleryItem(ndb.Model):
    id = ndb.StringProperty(required=True)
    path = ndb.StringProperty(required=True)
    title = ndb.StringProperty(required=True)
    type = ndb.StringProperty(required=True)
    description = ndb.StringProperty(required=True)
    rating = ndb.IntegerProperty(required=False)
    location = ndb.GeoPtProperty(required=False)
    children = ndb.StructuredProperty(ChildItem, repeated=True, required=False)
    resizes = ndb.StructuredProperty(ResizedImage, repeated=True, required=False)
    metadata = ndb.StructuredProperty(MetadataProperty, repeated=True, required=False)
    updated = ndb.DateTimeProperty(auto_now=True)
