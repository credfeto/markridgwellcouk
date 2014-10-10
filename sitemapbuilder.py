import datetime
import webapp2
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
from google.appengine.api import capabilities
from google.appengine.api import memcache

import models
import utils
import sync
import sys


def build_sitemap_index(host, expiry_seconds):
    memcachedKey = 'sitemap-index-output-' + host
    output = ''

    memcacheEnabled = capabilities.CapabilitySet('memcache').is_enabled()

    if memcacheEnabled:
        try:
            output = memcache.get(memcachedKey)
        except KeyError:
            output = ''

    if output is None or len(output) == 0:

        when = datetime.datetime.now()

        items = []

        items.append({'index': '0', 'lastMod': when})
        items.append({'index': '1', 'lastMod': when})
        items.append({'index': '2', 'lastMod': when})
        items.append({'index': '3', 'lastMod': when})
        items.append({'index': '4', 'lastMod': when})
        items.append({'index': '5', 'lastMod': when})
        items.append({'index': '6', 'lastMod': when})
        items.append({'index': '7', 'lastMod': when})
        items.append({'index': '8', 'lastMod': when})
        items.append({'index': '9', 'lastMod': when})
        items.append({'index': 'a', 'lastMod': when})
        items.append({'index': 'b', 'lastMod': when})
        items.append({'index': 'c', 'lastMod': when})
        items.append({'index': 'd', 'lastMod': when})
        items.append({'index': 'e', 'lastMod': when})
        items.append({'index': 'f', 'lastMod': when})

        template_vals = {'host': host, 'indexes': items}

        output = utils.render_template("sitemapindex.html", template_vals)

        if memcacheEnabled:
            memcache.set(memcachedKey, output, expiry_seconds)

    return output


def build_sitemap_section(host, key, expiry_seconds):
    memcacheEnabled = capabilities.CapabilitySet('memcache').is_enabled()

    memcachedKey = 'sitemap-section-' + key + '-output-' + host
    output = ''

    if memcacheEnabled:
        try:
            output = memcache.get(memcachedKey)
        except KeyError:
            output = ''

    if output is None or len(output) == 0:

        q = models.GeneratedItem.query(models.GeneratedItem.id == memcachedKey)
        pregenerated = q.get()
        if pregenerated is None:

            when = datetime.datetime.now()

            q = models.GalleryItem.query(models.GalleryItem.indexSection == key, projection=["path"]).order(
                models.GalleryItem.path)

            items = []
            for item in q:
                items.append({'path': item.path})

            template_vals = {'host': host, 'items': items}

            output = utils.render_template("sitemapsection.html", template_vals)

            pregenerated = models.GeneratedItem(
                id=memcachedKey,
                text=output,
                updated=when)
            pregenerated.put();
        else:
            output = pregenerated.text

        if memcacheEnabled:
            memcache.set(memcachedKey, output, expiry_seconds)

    return output