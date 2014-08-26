
from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb

import models
import utils
import sys
import datetime

def is_trackable( userAgent ):
    
    agent = userAgent.lower()

    if 'googlebot' in agent:
        return False

    if 'msnbot' in agent:
        return False

    if 'bingbot' in agent:
        return False

    if 'chrome' in agent:
        return True

    if 'safari' in agent:
        return True

    if 'opera' in agent:
        return True

    if 'trident' in agent:
        return True

    if 'firefox' in agent:
        return True

    return False


def record_view( id, path ):
    q = models.ItemViewCount.query(models.ItemViewCount.id == id)
    

    dbItem = q.get()
    if dbItem is None:
        dbItem = models.ItemViewCount(
                            id = id,
                            path = path,
                            viewCount = 1)

        dbItem.put()

    else:
        dbItem.viewCount = dbItem.viewCount + 1
        dbItem.updated = datetime.datetime.now()

        dbItem.put()

    return dbItem.viewCount
    