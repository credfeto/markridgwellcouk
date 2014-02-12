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
from google.appengine.api import memcache

import models
import utils

def invalidateOutputCaches():
    memcache.delete('rss-output')

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

def sibling_changed( current, toupdate ):

    if current is None and toupdate is None:
        return False

    if current <> None and toupdate is None:
        return True

    if current is None and toupdate <> None:
        return True

    if current.id <> toupdate.id:
        return True

    if current.title <> toupdate.title:
        return True

    if current.type <> toupdate.type:
        return True

    if current.description <> toupdate.description:
        return True

    if current.type == 'photo':
        if current.thumbnail.width <> toupdate.thumbnail.width:
            return True

        if current.thumbnail.height <> toupdate.thumbnail.height:
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

def metadata_changed( current, toupdate ):

    if len( current ) <> len(toupdate):
        return True

    for (i, currentMetadata ) in enumerate(current):
        newMetadata = toupdate[i]

        if currentMetadata.name <> newMetadata.name:
            return True

        if currentMetadata.value <> newMetadata.value:
            return True

    return False

def keywords_changed( current, toupdate ):

    if len( current ) <> len(toupdate):
        return True

    for (i, currentKeyword ) in enumerate(current):
        newKeyword = toupdate[i]

        if currentKeyword <> newKeyword:
            return True

    return False


def synchronize():
    url = utils.site_url('/site.js')
    url = 'E:\\Gallery\\LiveImages\\site.js'
    url = 'E:\\GalleryMetadata\\site.js'

    #sys.stdout.write('\n\n')
    #sys.stdout.write('Downloading from: ' + url + '\n');

    #result = urlfetch.fetch(url);
    #if result.status_code == 200:

    #    contents = result.content
    #    #sys.stdout.write(contents+ '\n\n')
    with open(url, "r") as myfile:
        contents = myfile.read()
        myfile.close()
        synchronize_common( contents)

def synchronize_url():
    url = utils.site_url('/site.js')
    url = 'http://localhost/GalleryMetadata/site.js'

    #sys.stdout.write('\n\n')
    #sys.stdout.write('Downloading from: ' + url + '\n');

    result = urlfetch.fetch(url);
    if result.status_code == 200:

        contents = result.content
        synchronize_common( contents)

def synchronize_common(contents):
    decoded = json.loads(contents)
    version = decoded["version"]

    itemsWritten = 0

    #sys.stdout.write("Decoded Version: " + str(version) + '\n' )

    for item in decoded["items"]:
        path = item["Path"]
        title = item["Title"]
        type = item["Type"]
        description = item["Description"]
        rating = None #item["Rating"]
        

        hash = utils.generate_url_hash(path)
        indexSection = hash[:1]

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

        metadata = None
        metadataItems = item['Metadata']
        if metadataItems <> None:
            metadata = []
            for mdItem in metadataItems:
                mdName = mdItem['Name']
                mdValue = mdItem['Value']

                metadata.append( models.MetadataProperty(
                                                name = mdName,
                                                value = mdValue
                                                ) )

        keywords = item['Keywords']

        #sys.stdout.write("Path: " + path + '\n' )
        #sys.stdout.write("Hash: " + hash + '\n' )

        foundImageSizes = None
        imageSizes = item["ImageSizes"]
        if imageSizes <> None:
            foundImageSizes = []
            for imageSize in imageSizes:                            
                imageSizeWidth = imageSize["Width"]
                imageSizeHeight = imageSize["Height"]
                #sys.stdout.write(" * Size: " + str( imageSizeWidth) + "x" + str( imageSizeHeight) + '\n' )
                foundImageSizes.append( models.ResizedImage(
                                                                width = imageSizeWidth,
                                                                height = imageSizeHeight
                                                            ) )


                
        firstSibling = None
        fsibling = item["First"]
        if fsibling <> None:
                    childPath = fsibling["Path"]
                    childHash = utils.generate_url_hash(childPath)
                    childTitle = fsibling["Title"]
                    childType = fsibling["Type"]
                    childDescription = fsibling["Description"]
                            
                    foundThumbnailSize = None
                    childImageSizes = fsibling["ImageSizes"]
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

                    firstSibling = models.ChildItem(
                                                    id = childHash,
                                                    path = childPath,
                                                    title = childTitle,
                                                    type = childType,
                                                    description = childDescription,
                                                    thumbnail = foundThumbnailSize
                                                )


        previousSibling = None
        psibling = item["Previous"]
        if psibling <> None:
                    childPath = psibling["Path"]
                    childHash = utils.generate_url_hash(childPath)
                    childTitle = psibling["Title"]
                    childType = psibling["Type"]
                    childDescription = psibling["Description"]
                            
                    foundThumbnailSize = None
                    childImageSizes = psibling["ImageSizes"]
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

                    previousSibling = models.ChildItem(
                                                    id = childHash,
                                                    path = childPath,
                                                    title = childTitle,
                                                    type = childType,
                                                    description = childDescription,
                                                    thumbnail = foundThumbnailSize
                                                )

        nextSibling = None
        nsibling = item["Next"]
        if nsibling <> None:
                    childPath = nsibling["Path"]
                    childHash = utils.generate_url_hash(childPath)
                    childTitle = nsibling["Title"]
                    childType = nsibling["Type"]
                    childDescription = nsibling["Description"]
                            
                    foundThumbnailSize = None
                    childImageSizes = nsibling["ImageSizes"]
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

                    nextSibling = models.ChildItem(
                                                    id = childHash,
                                                    path = childPath,
                                                    title = childTitle,
                                                    type = childType,
                                                    description = childDescription,
                                                    thumbnail = foundThumbnailSize
                                                )

        lastSibling = None
        lsibling = item["Last"]
        if lsibling <> None:
                    childPath = lsibling["Path"]
                    childHash = utils.generate_url_hash(childPath)
                    childTitle = lsibling["Title"]
                    childType = lsibling["Type"]
                    childDescription = lsibling["Description"]
                            
                    foundThumbnailSize = None
                    childImageSizes = lsibling["ImageSizes"]
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

                    lastSibling = models.ChildItem(
                                                    id = childHash,
                                                    path = childPath,
                                                    title = childTitle,
                                                    type = childType,
                                                    description = childDescription,
                                                    thumbnail = foundThumbnailSize
                                                )


        q = models.GalleryItem.query(models.GalleryItem.id == hash)

        dbItem = q.get()
        if dbItem is None:
            dbItem = models.GalleryItem(
                                        id = hash,
                                        path = path,
                                        indexSection = indexSection,
                                        title = title,
                                        type = type,
                                        description = description,
                                        rating = rating,
                                        location = location,
                                        children = children,
                                        resizes = foundImageSizes,
                                        metadata = metadata,
                                        keywords = keywords,
                                        firstSibling = firstSibling,
                                        previousSibling = previousSibling,
                                        nextSibling = nextSibling,
                                        lastSibling = lastSibling
                                        )
            dbItem.put()
                
            itemsWritten = itemsWritten + 1
            #sys.stdout.write('Created\n')
        else:

            if path <> dbItem.path or indexSection <> dbItem.indexSection or  dbItem.title <> title or dbItem.type <> type or dbItem.description <> description or dbItem.location <> location or children_changed( dbItem.children, children ) or resizes_changed( dbItem.resizes, foundImageSizes ) or metadata_changed( dbItem.metadata, metadata ) or keywords_changed( dbItem.keywords, keywords ) or sibling_changed( dbItem.firstSibling, firstSibling )or sibling_changed( dbItem.previousSibling, previousSibling )or sibling_changed( dbItem.nextSibling, nextSibling )or sibling_changed( dbItem.lastSibling, lastSibling ):
                dbItem.path = path
                dbItem.indexSection = indexSection
                dbItem.title = title
                dbItem.type = type
                dbItem.description = description
                dbItem.rating = rating
                dbItem.location = location
                dbItem.children = children
                dbItem.resizes = foundImageSizes
                dbItem.metadata = metadata
                dbItem.keywords = keywords
                dbItem.firstSibling = firstSibling
                dbItem.previousSibling = previousSibling
                dbItem.nextSibling = nextSibling
                dbItem.lastSibling = lastSibling
                dbItem.updated = datetime.datetime.now()

                dbItem.put()
                    
                itemsWritten = itemsWritten + 1
                #sys.stdout.write('Updated\n')
            #else:
                #sys.stdout.write('Unchanged\n')
        #sys.stdout.write('\n')
    
    for deletedItem in decoded["deletedItems"]:
        #sys.stdout.write('Item: ' + deletedItem + '\n')
        hash = utils.generate_url_hash(deletedItem)

        q = models.GalleryItem.query(models.GalleryItem.id == hash)

        dbItem = q.get()
        if dbItem <> None:
            itemsWritten = itemsWritten + 1
            dbItem.key.delete()
            #sys.stdout.write('Deleted\n')

    if itemsWritten > 0:
        invalidateOutputCaches()

    return itemsWritten