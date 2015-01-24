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
from google.appengine.api import capabilities

import models
import utils
import pubsubhubub
import logging


def invalidateGeneratedItems():
    invalidateGeneratedItem('rss-output')
    invalidateGeneratedItem('sitemap-index-output')
    invalidateGeneratedItem('sitemap-section-0-output')
    invalidateGeneratedItem('sitemap-section-1-output')
    invalidateGeneratedItem('sitemap-section-2-output')
    invalidateGeneratedItem('sitemap-section-3-output')
    invalidateGeneratedItem('sitemap-section-4-output')
    invalidateGeneratedItem('sitemap-section-5-output')
    invalidateGeneratedItem('sitemap-section-6-output')
    invalidateGeneratedItem('sitemap-section-7-output')
    invalidateGeneratedItem('sitemap-section-8-output')
    invalidateGeneratedItem('sitemap-section-9-output')
    invalidateGeneratedItem('sitemap-section-a-output')
    invalidateGeneratedItem('sitemap-section-b-output')
    invalidateGeneratedItem('sitemap-section-c-output')
    invalidateGeneratedItem('sitemap-section-d-output')
    invalidateGeneratedItem('sitemap-section-e-output')
    invalidateGeneratedItem('sitemap-section-f-output')


def invalidateGeneratedItem(key):
    q = models.GeneratedItem.query(models.GeneratedItem.id == key)
    dbItem = q.get()
    if dbItem <> None:
        dbItem.key.delete()


def invalidateOutputCaches():
    memcacheEnabled = capabilities.CapabilitySet('memcache').is_enabled()

    if memcacheEnabled:
        memcache.delete('rss-output')
        memcache.delete('sitemap-index-output')
        memcache.delete('sitemap-section-0-output')
        memcache.delete('sitemap-section-1-output')
        memcache.delete('sitemap-section-2-output')
        memcache.delete('sitemap-section-3-output')
        memcache.delete('sitemap-section-4-output')
        memcache.delete('sitemap-section-5-output')
        memcache.delete('sitemap-section-6-output')
        memcache.delete('sitemap-section-7-output')
        memcache.delete('sitemap-section-8-output')
        memcache.delete('sitemap-section-9-output')
        memcache.delete('sitemap-section-a-output')
        memcache.delete('sitemap-section-b-output')
        memcache.delete('sitemap-section-c-output')
        memcache.delete('sitemap-section-d-output')
        memcache.delete('sitemap-section-e-output')
        memcache.delete('sitemap-section-f-output')

    invalidateGeneratedItems()


def children_changed(current, toupdate):
    if len(current) <> len(toupdate):
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

        if currentChild.path <> newChild.path:
            return True

        if currentChild.originalAlbumPath <> newChild.originalAlbumPath:
            return True

        if currentChild.type == 'photo':
            if currentChild.thumbnail.width <> newChild.thumbnail.width:
                return True

            if currentChild.thumbnail.height <> newChild.thumbnail.height:
                return True

    return False


def breadcrumbs_changed(current, toupdate):
    if len(current) <> len(toupdate):
        return True

    for (i, currentCrumb ) in enumerate(current):
        newCrumb = toupdate[i]

        if currentCrumb.id <> newCrumb.id:
            return True

        if currentCrumb.title <> newCrumb.title:
            return True

        if currentCrumb.description <> newCrumb.description:
            return True

    return False


def sibling_changed(current, toupdate):
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


def resizes_changed(current, toupdate):
    if len(current) <> len(toupdate):
        return True

    for (i, currentSize ) in enumerate(current):
        newSize = toupdate[i]

        if currentSize.width <> newSize.width:
            return True

        if currentSize.height <> newSize.height:
            return True

    return False


def metadata_changed(current, toupdate):
    if len(current) <> len(toupdate):
        return True

    for (i, currentMetadata ) in enumerate(current):
        newMetadata = toupdate[i]

        if currentMetadata.name <> newMetadata.name:
            return True

        if currentMetadata.value <> newMetadata.value:
            return True

    return False


def keywords_changed(current, toupdate):
    if len(current) <> len(toupdate):
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

    # sys.stdout.write('\n\n')
    #sys.stdout.write('Downloading from: ' + url + '\n');

    #result = urlfetch.fetch(url);
    #if result.status_code == 200:

    #    contents = result.content
    #    #sys.stdout.write(contents+ '\n\n')
    with open(url, "r") as myfile:
        contents = myfile.read()
        myfile.close()
        synchronize_common(contents)


def synchronize_url():
    url = utils.site_url('/site.js')
    url = 'http://localhost/GalleryMetadata/site.js'

    # sys.stdout.write('\n\n')
    #sys.stdout.write('Downloading from: ' + url + '\n');

    result = urlfetch.fetch(url);
    if result.status_code == 200:
        contents = result.content
        synchronize_common(contents)


def extract_location(item):
    location = None
    loc = item["Location"]
    if loc <> None:
        if "Latitude" in loc and "Longitude" in loc:
            lat = loc["Latitude"]
            lng = loc["Longitude"]
            location = ndb.GeoPt(lat, lng)
    return location


def extract_children(item):
    children = None
    childItems = item["Children"]
    if childItems <> None:
        children = []
        for child in childItems:
            childPath = child["Path"]
            childOriginalAlbumPath = child["OriginalAlbumPath"]
            if childOriginalAlbumPath is None:
                childOriginalAlbumPath = ''
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

                    if ( childImageWidth == 0 or childImageSizeWidth < childImageWidth) and (
                            childImageHeight == 0 or childImageSizeHeight < childImageHeight):
                        childImageWidth = childImageSizeWidth
                        childImageHeight = childImageSizeHeight

                if childImageWidth <> 0 and childImageHeight <> 0:
                    foundThumbnailSize = models.ResizedImage(
                        width=childImageWidth,
                        height=childImageHeight)

            children.append(models.ChildItem(
                id=childHash,
                path=childPath,
                originalAlbumPath=childOriginalAlbumPath,
                title=childTitle,
                type=childType,
                description=childDescription,
                thumbnail=foundThumbnailSize
            ))

    return children


def extract_breadcrumbs(item):
    breadcrumbs = None
    breadcrumbItems = item["Breadcrumbs"]
    if breadcrumbItems <> None:
        breadcrumbs = []
        for crumb in breadcrumbItems:
            crumbPath = crumb["Path"]
            crumbHash = utils.generate_url_hash(crumbPath)
            crumbTitle = crumb["Title"]
            crumbDescription = crumb["Description"]

            breadcrumbs.append(models.BreadcrumbItem(
                id=crumbHash,
                path=crumbPath,
                title=crumbTitle
            ))

    return breadcrumbs


def extract_metadata(item):
    metadata = None
    metadataItems = item['Metadata']
    if metadataItems <> None:
        metadata = []
        for mdItem in metadataItems:
            mdName = mdItem['Name']
            mdValue = mdItem['Value']

            metadata.append(models.MetadataProperty(
                name=mdName,
                value=mdValue
            ))

    return metadata


def extract_keywords(item):
    return item['Keywords']


def extract_image_sizes(item):
    foundImageSizes = None
    imageSizes = item["ImageSizes"]
    if imageSizes <> None:
        foundImageSizes = []
        for imageSize in imageSizes:
            imageSizeWidth = imageSize["Width"]
            imageSizeHeight = imageSize["Height"]
            # sys.stdout.write(" * Size: " + str( imageSizeWidth) + "x" + str( imageSizeHeight) + '\n' )
            foundImageSizes.append(models.ResizedImage(
                width=imageSizeWidth,
                height=imageSizeHeight
            ))

    return foundImageSizes;


def extract_sibling(item, which):
    firstSibling = None
    fsibling = item[which]
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

                if ( childImageWidth == 0 or childImageSizeWidth < childImageWidth) and (
                        childImageHeight == 0 or childImageSizeHeight < childImageHeight):
                    childImageWidth = childImageSizeWidth
                    childImageHeight = childImageSizeHeight

            if childImageWidth <> 0 and childImageHeight <> 0:
                foundThumbnailSize = models.ResizedImage(
                    width=childImageWidth,
                    height=childImageHeight)

        firstSibling = models.ChildItem(
            id=childHash,
            path=childPath,
            title=childTitle,
            type=childType,
            description=childDescription,
            thumbnail=foundThumbnailSize
        )
    return firstSibling


def delete_item(hash):
    q = models.GalleryItem.query(models.GalleryItem.id == hash)

    dbItem = q.get()
    if dbItem <> None:
        dbItem.key.delete()
        # sys.stdout.write('Deleted\n')
        return True

    return False


def delete_published_item(hash):
    piq = models.PublishableItem.query(models.PublishableItem.id == hash)
    pi = piq.get()
    if pi <> None:
        pi.key.delete()


def synchronize_common(contents):
    decoded = json.loads(contents)
    version = decoded["version"]

    itemsWritten = 0

    logging.info("Decoded Version: " + str(version))

    for item in decoded["items"]:

        path = item["Path"]
        originalAlbumPath = item["OriginalAlbumPath"]
        if originalAlbumPath is None:
            originalAlbumPath = ''
        title = item["Title"]
        type = item["Type"]
        description = item["Description"]
        rating = None  # item["Rating"]

        hash = utils.generate_url_hash(path)
        indexSection = hash[:1]

        location = extract_location(item)
        children = extract_children(item)
        breadcrumbs = extract_breadcrumbs(item)
        metadata = extract_metadata(item)
        keywords = extract_keywords(item)
        foundImageSizes = extract_image_sizes(item)
        firstSibling = extract_sibling(item, "First")
        previousSibling = extract_sibling(item, "Previous")
        nextSibling = extract_sibling(item, "Next")
        lastSibling = extract_sibling(item, "Last")

        q = models.GalleryItem.query(models.GalleryItem.id == hash)

        dbItem = q.get()
        if dbItem is None:
            dbItem = models.GalleryItem(
                id=hash,
                path=path,
                originalAlbumPath=originalAlbumPath,
                indexSection=indexSection,
                title=title,
                type=type,
                description=description,
                rating=rating,
                location=location,
                children=children,
                breadcrumbs=breadcrumbs,
                resizes=foundImageSizes,
                metadata=metadata,
                keywords=keywords,
                firstSibling=firstSibling,
                previousSibling=previousSibling,
                nextSibling=nextSibling,
                lastSibling=lastSibling
            )
            dbItem.put()

            itemsWritten = itemsWritten + 1
            logging.info('Created: ' + path)

            if type == 'photo' and utils.is_public_publishable_path(path) and utils.is_publishable(dbItem):
                publishItem = models.PublishableItem(id=dbItem.id)
                publishItem.put()

        else:

            if path <> dbItem.path or originalAlbumPath <> dbItem.originalAlbumPath or indexSection <> dbItem.indexSection or dbItem.title <> title or dbItem.type <> type or dbItem.description <> description or dbItem.location <> location or children_changed(
                    dbItem.children, children) or breadcrumbs_changed(dbItem.breadcrumbs, breadcrumbs) or resizes_changed(dbItem.resizes,
                                                                                                      foundImageSizes) or metadata_changed(
                    dbItem.metadata, metadata) or keywords_changed(dbItem.keywords, keywords) or sibling_changed(
                    dbItem.firstSibling, firstSibling) or sibling_changed(dbItem.previousSibling,
                                                                          previousSibling) or sibling_changed(
                    dbItem.nextSibling, nextSibling) or sibling_changed(dbItem.lastSibling, lastSibling):
                dbItem.path = path
                dbItem.originalAlbumPath = originalAlbumPath
                dbItem.indexSection = indexSection
                dbItem.title = title
                dbItem.type = type
                dbItem.description = description
                dbItem.rating = rating
                dbItem.location = location
                dbItem.children = children
                dbItem.breadcrumbs = breadcrumbs
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
                logging.info('updated: ' + path)
            else:
                logging.info('Unchanged: ' + path)

    for deletedItem in decoded["deletedItems"]:
        logging.info('Deleting: ' + deletedItem)
        hash = utils.generate_url_hash(deletedItem)

        if delete_item(hash):
            itemsWritten = itemsWritten + 1

        delete_published_item(hash)

    if itemsWritten > 0:
        invalidateOutputCaches()
        pubsubhubub.queue_update()

    return itemsWritten