import datetime
import webapp2
import json
from collections import defaultdict

from google.appengine.api import mail
from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.ext import db

import models
import utils
import tracking
import itemnaming
import logging

import sys
sys.path.insert(0, 'lib')

import markdown

class IndexHandler(webapp2.RequestHandler):
    def get(self):

        host = self.request.host_url

        userAgent = self.request.headers.get('User-Agent', None)

        if utils.is_development() == False and self.request.scheme == 'http' and utils.device_supports_ssl_tni(userAgent):
            self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
            self.response.headers['Pragma'] = 'public'
            self.redirect(utils.redirect_url(self.request.path, self.request.query_string), permanent=True)

        windowsshare = utils.enable_windows_share_metadata(userAgent)
        searchPath = self.request.path.lower()

        hash = utils.generate_url_hash(searchPath)

        q = models.GalleryItem.query(models.GalleryItem.id == hash)

        track = utils.should_track(self.request.headers)
        if track:
            logging.info('Tracking: Enabled')
        else:
            logging.info('Tracking: Disabled')

        item = q.get()
        if item is None:
            newSearchPath = utils.convert_old_url(searchPath)

            shouldReportError = True
            if newSearchPath <> searchPath:
                hash = utils.generate_url_hash(newSearchPath)
                searchPath = newSearchPath
                q = models.GalleryItem.query(models.GalleryItem.id == hash)
                item = q.get()

                if item <> None:
                    shouldReportError = False
                    utils.add_response_headers(self.request, self.response.headers)
                    self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
                    self.response.headers['Pragma'] = 'public'
                    self.redirect(utils.redirect_url(newSearchPath, self.request.query_string), permanent=True)

            if shouldReportError:
                template_vals = {'host': self.request.host_url, 'path': searchPath, 'track': track, 'hash': hash,
                                 'users': users, 'showShare': False, 'windowsshare': windowsshare}
                utils.add_response_headers(self.request, self.response.headers)
                self.response.out.write(utils.render_template("notfound.html", template_vals))
                self.response.set_status(404)
        else:
            children = None
            if item.children:
                children = []
                for child in item.children:
                    thumbnailUrl = None
                    if child.thumbnail:
                        base_child_image_path = child.path
                        if child.originalAlbumPath:
                            base_child_image_path = child.originalAlbumPath

                        thumbnailUrl = utils.image_url(
                            base_child_image_path, child.thumbnail)
                    tagId = utils.path_to_tagId(child.path)
                    childItem = {'id': child.id, 'path': child.path, 'title': child.title, 'type': child.type,
                                 'description': child.description, 'thumbnail': child.thumbnail,
                                 'thumbnailUrl': thumbnailUrl, "tagId": tagId}
                    children.append(childItem)

            parentItemUrl = None
            breadcrumbs = None
            if item.breadcrumbs:
                breadcrumbs = []
                lastCrumbTagId = utils.path_to_tagId(item.path)
                for crumb in reversed(item.breadcrumbs):
                    if parentItemUrl is None:
                        parentItemUrl = host + crumb.path
                    tagId = utils.path_to_tagId(crumb.path)
                    crumbItem = {'id': crumb.id, 'path': crumb.path, 'title': crumb.title,
                                 'description': crumb.description, "tagId": lastCrumbTagId}
                    breadcrumbs.insert(0, crumbItem)
                    lastCrumbTagId = tagId
            if parentItemUrl is None:
                parentItemUrl = host

            resizecss = None;
            thumbnailImageUrl = None
            imageUrl = None
            imageWidth = None
            imageHeight = None
            if item.resizes:

                orderedResizes = sorted(item.resizes, key=lambda r: r.width)

                css = utils.build_image_css(item, orderedResizes)
                if css is None:
                    first = None
                    last = None
                    resizecss = None
                else:
                    first = css['first']
                    last = css['last']
                    resizecss = '<style>' + css['css'] + '</style>'

                if first is None:
                    resizecss = ''
                else:
                    thumbnailImageUrl = utils.image_url(item.path, first)

                    imageUrl = utils.image_url(item.path, last)
                    imageWidth = last.width
                    imageHeight = last.height;

            firstSibling = None
            previousSibling = None
            nextSibling = None
            lastSibling = None

            if item.firstSibling <> None:
                firstSibling = {'title': item.firstSibling.title, 'url': item.firstSibling.path}

            if item.previousSibling <> None:
                previousSibling = {'title': item.previousSibling.title, 'url': item.previousSibling.path}

            if item.nextSibling <> None:
                nextSibling = {'title': item.nextSibling.title, 'url': item.nextSibling.path}

            if item.lastSibling <> None:
                lastSibling = {'title': item.lastSibling.title, 'url': item.lastSibling.path}

            keywords = None
            if item.keywords:
                keywords = ",".join(item.keywords)

            showShare = utils.should_share(userAgent)

            views = 0
            if item.resizes:

                if tracking.is_sharing_callback(userAgent):
                    views = tracking.record_share(item.id, item.path)
                else:
                    if tracking.is_trackable(userAgent):
                        views = tracking.record_view(item.id, item.path)

            originalAlbumPath = ''
            title = item.title
            if children is None:
                title = itemnaming.photo_title(item, 10000)

                if item.originalAlbumPath:
                    originalAlbumPath = item.originalAlbumPath

            description = ""
            if item.description:
                md = markdown.Markdown()
                description = md.convert(item.description)

            template_vals = {'host': host, 'path': searchPath, 'track': track, 'hash': hash, 'users': users,
                             'title': title, 'item': item, 'children': children, 'breadcrumbs': breadcrumbs,
                             'resizecss': resizecss, 'staticurl': self.request.relative_url('/static'),
                             'thumbnailUrl': thumbnailImageUrl, 'fullImageUrl': imageUrl, 'fullImageWidth': imageWidth,
                             'fullImageHeight': imageHeight, 'firstSibling': firstSibling,
                             'previousSibling': previousSibling, 'nextSibling': nextSibling, 'lastSibling': lastSibling,
                             'keywords': keywords, 'showShare': showShare, 'windowsshare': windowsshare,
                             'parentItemUrl': parentItemUrl,
                             'description': description, 'originalAlbumPath': originalAlbumPath}
            if children is None:
                self.response.out.write(utils.render_template("photo.html", template_vals))
            else:
                self.response.out.write(utils.render_template("index.html", template_vals))

            utils.add_response_headers(self.request, self.response.headers)
            self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
            self.response.headers['Pragma'] = 'public'
            self.response.headers['X-PageViews'] = str(views)

class LegacyImageIndexHandler(webapp2.RequestHandler):
    def get(self):

        host = self.request.host_url

        userAgent = self.request.headers.get('User-Agent', None)

        if utils.is_development() == False and self.request.scheme == 'http' and utils.device_supports_ssl_tni(userAgent):
            self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
            self.response.headers['Pragma'] = 'public'
            self.redirect(utils.redirect_url(self.request.path, self.request.query_string), permanent=True)

        windowsshare = utils.enable_windows_share_metadata(userAgent)
        searchPath = self.request.path.lower()

        newSearchPath = utils.convert_old_url(searchPath)

        logging.info('Redirect to: ' + newSearchPath)

        utils.add_response_headers(self.request, self.response.headers)
        self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
        self.response.headers['Pragma'] = 'public'
        self.redirect(utils.redirect_url(newSearchPath, self.request.query_string), permanent=True)


app = webapp2.WSGIApplication([
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', LegacyImageIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', LegacyImageIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', LegacyImageIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', LegacyImageIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', LegacyImageIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', LegacyImageIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', LegacyImageIndexHandler),
    ('/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', LegacyImageIndexHandler),
    ('/[\w\-]*/[0-9]+_image\.jpg', LegacyImageIndexHandler),
    ('/[0-9]+_image\.jpg', LegacyImageIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/[\w\-]*/', IndexHandler),
    ('/[\w\-]*/', IndexHandler),
    ('/', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/~[0-9]+', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/~[0-9]+', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/~[0-9]+', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/~[0-9]+', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/~[0-9]+', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/~[0-9]+', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/~[0-9]+', IndexHandler),
    ('/[\w\-]*/[\w\-]*/~[0-9]+', IndexHandler),
    ('/[\w\-]*/~[0-9]+', IndexHandler),
    ('/~[0-9]+', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*', IndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*', IndexHandler),
    ('/[\w\-]*/[\w\-]*', IndexHandler),
    ('/[\w\-]*', IndexHandler),
])