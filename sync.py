import datetime
import sys
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
from google.appengine.api import urlfetch 

import models
import utils

def children_changed( current, toupdate ):

    if len( current ) <> len(toupdate):
        return True

    for (i, currentChild ) in enumerate(current):
        newChild = toupdate[i]

        if currentChild.id <> newChild.id:
            return True

        if currentChild.title <> newChild.title:
            return True

        if currentChild.type <> newChild.type:
            return True

        if currentChild.description <> newChild.description:
            return True

        if currentChild.type == 'photo':
            if currentChild.thumbnail.width <> newChild.thumbnail.width:
                return True

            if currentChild.thumbnail.height <> newChild.thumbnail.height:
                return True

    return False


def resizes_changed( current, toupdate ):

    if len( current ) <> len(toupdate):
        return True

    for (i, currentSize ) in enumerate(current):
        newSize = toupdate[i]

        if currentSize.width <> newSize.width:
            return True

        if currentSize.height <> newSize.height:
            return True

    return False


def synchronize():
    url = utils.site_url('/site.js')

    sys.stdout.write('Downloading from: ' + url + '\n');

    result = urlfetch.fetch(url);
    if result.status_code == 200:
        #sys.stdout.write(result.content+ '\n\n')

        decoded = json.loads(result.content)
        version = decoded["version"]

        sys.stdout.write("Decoded Version: " + str(version) + '\n' )

        for item in decoded["items"]:
            path = item["Path"]
            title = item["Title"]
            type = item["Type"]
            description = item["Description"]
            rating = None #item["Rating"]

            hash = utils.generate_url_hash(path)

            location = None
            loc = item["Location"]
            if loc <> None:
                if "Latitude" in loc and "Longitude" in loc:
                    lat = loc["Latitude"]
                    lng = loc["Latitude"]
                    location = ndb.GeoPt( lat, lng )
                

            children = None
            childItems = item["Children"]
            if childItems <> None:
                children = []
                for child in childItems:
                        childPath = child["Path"]
                        childHash = utils.generate_url_hash(childPath)
                        childTitle = child["Title"]
                        childType = child["Type"]
                        childDescription = child["Description"]
                            
                        foundThumbnailSize = None
                        childImageSizes = child["ImageSizes"]
                        if childImageSizes <> None:
                            childImageWidth = 0
                            childImageHeight = 0
                                
                            for childImageSize in childImageSizes:
                                childImageSizeWidth = childImageSize["Width"]
                                childImageSizeHeight = childImageSize["Height"]

                                if ( childImageWidth == 0 or childImageSizeWidth < childImageWidth) and ( childImageHeight == 0 or childImageSizeHeight < childImageHeight):
                                    childImageWidth = childImageSizeWidth
                                    childImageHeight = childImageSizeHeight
                                    
                            if childImageWidth <> 0 and childImageHeight <> 0:
                                foundThumbnailSize = models.ResizedImage(
                                                                                width = childImageWidth,
                                                                                height = childImageHeight )

                        children.append( models.ChildItem(
                                                        id = childHash,
                                                        path = childPath,
                                                        title = childTitle,
                                                        type = childType,
                                                        description = childDescription,
                                                        thumbnail = foundThumbnailSize
                                                    ) )

            sys.stdout.write("Path: " + path + '\n' )
            sys.stdout.write("Hash: " + hash + '\n' )

            foundImageSizes = None
            imageSizes = item["ImageSizes"]
            if imageSizes <> None:
                foundImageSizes = []
                for imageSize in imageSizes:                            
                    imageSizeWidth = imageSize["Width"]
                    imageSizeHeight = imageSize["Height"]
                    sys.stdout.write(" * Size: " + str( imageSizeWidth) + "x" + str( imageSizeHeight) + '\n' )
                    foundImageSizes.append( models.ResizedImage(
                                                                    width = imageSizeWidth,
                                                                    height = imageSizeHeight
                                                                ) )


                

            q = models.GalleryItem.query(models.GalleryItem.id == hash)

            dbItem = q.get()
            if dbItem is None:
                dbItem = models.GalleryItem(
                                            id = hash,
                                            path = path,
                                            title = title,
                                            type = type,
                                            description = description,
                                            rating = rating,
                                            location = location,
                                            children = children,
                                            resizes = foundImageSizes
                                            )
                dbItem.put()
                sys.stdout.write('Created\n')
            else:

                if path <> dbItem.path or dbItem.title <> title or dbItem.type <> type or dbItem.description <> description or dbItem.location <> location or children_changed( dbItem.children, children ) or resizes_changed( dbItem.resizes, foundImageSizes ):
                    dbItem.path = path
                    dbItem.title = title
                    dbItem.type = type
                    dbItem.description = description
                    dbItem.rating = rating
                    dbItem.location = location
                    dbItem.children = children
                    dbItem.resizes = foundImageSizes

                    dbItem.put()

                    sys.stdout.write('Updated\n')
                else:
                    sys.stdout.write('Unchanged\n')
            sys.stdout.write('\n')
