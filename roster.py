from google.appengine.ext import ndb

import models

def add_contact(email):

    item = models.Subscriber.query(models.Subscriber.id == email).get()

    if item is None:
        item = models.Subscriber( id = email )
        item.put()

def remove_contact(email):

    item = models.Subscriber.query(models.Subscriber.id == email).get()

    if item is not None:
        item.key.delete()
