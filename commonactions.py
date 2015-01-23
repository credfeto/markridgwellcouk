from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
from google.appengine.api import mail

import models
import utils
import sys
from google.appengine.api import xmpp


def delete_item_from_publish_queue(id):
        status = ''

        publish = models.PublishableItem.query(models.PublishableItem.id == id).get()
        if publish is not None:

            item = models.GalleryItem.query(models.GalleryItem.id == id).get()

            # Remove the item
            publish.key.delete()

            if item is not None:
                 return 'Deleted: ' + item.path

            return 'Deleted: Unknown'

        else:
            return 'Item Not Found'

