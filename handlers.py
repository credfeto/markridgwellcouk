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

import random
import markdown

class IndexHandler(webapp2.RequestHandler):
    def get(self):

        host = self.request.host_url

        user_agent = self.request.headers.get('User-Agent', None)

        if utils.is_development() == False:
            if self.request.scheme == 'http' and utils.device_supports_ssl_tni(user_agent):
                self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
                self.response.headers['Pragma'] = 'public'
                self.redirect(utils.redirect_url(self.request.path, self.request.query_string), permanent=True)

            if host != 'http://www.markridgwell.co.uk' and host != 'https://www.markridgwell.co.uk':
                self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
                self.response.headers['Pragma'] = 'public'
                self.redirect(utils.redirect_url(self.request.path, self.request.query_string), permanent=True)
                return



        windows_share = utils.enable_windows_share_metadata(user_agent)
        search_path = self.request.path.lower()

        hash = utils.generate_url_hash(search_path)

        q = models.GalleryItem.query(models.GalleryItem.id == hash)

        track = utils.should_track(self.request.headers)
        if track:
            logging.info('Tracking: Enabled')
        else:
            logging.info('Tracking: Disabled')

        item = q.get()
        if item is None:
            new_search_path = utils.convert_old_url(search_path)

            should_report_error = True
            if new_search_path <> search_path:
                hash = utils.generate_url_hash(new_search_path)
                search_path = new_search_path
                q = models.GalleryItem.query(models.GalleryItem.id == hash)
                item = q.get()

                if item is not None:
                    should_report_error = False
                    utils.add_response_headers(self.request, self.response.headers)
                    self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
                    self.response.headers['Pragma'] = 'public'
                    self.redirect(utils.redirect_url(new_search_path, self.request.query_string), permanent=True)

            if should_report_error:
                template_vals = {'host': self.request.host_url, 'path': search_path, 'track': track, 'hash': hash,
                                 'users': users, 'showShare': False, 'windowsShare': windows_share}
                utils.add_response_headers(self.request, self.response.headers)
                self.response.out.write(utils.render_template("notfound.html", template_vals))
                self.response.set_status(404)
        else:
            children = None
            if item.children:
                children = []
                for child in item.children:
                    thumbnail_url = None
                    if child.thumbnail:
                        base_child_image_path = child.path
                        if child.originalAlbumPath:
                            base_child_image_path = child.originalAlbumPath

                        thumbnail_url = utils.image_url(
                            base_child_image_path, child.thumbnail)
                    tag_id = utils.path_to_tagId(child.path)
                    childItem = {'id': child.id, 'path': child.path, 'title': child.title, 'type': child.type,
                                 'description': child.description, 'thumbnail': child.thumbnail,
                                 'thumbnailUrl': thumbnail_url, "tagId": tag_id}
                    children.append(childItem)

            parent_item_url = None
            breadcrumbs = None
            if item.breadcrumbs:
                breadcrumbs = []
                last_crumb_tag_id = utils.path_to_tagId(item.path)
                for crumb in reversed(item.breadcrumbs):
                    if parent_item_url is None:
                        parent_item_url = host + crumb.path
                    tag_id = utils.path_to_tagId(crumb.path)
                    crumb_item = {'id': crumb.id, 'path': crumb.path, 'title': crumb.title, 'description': crumb.description, "tagId": last_crumb_tag_id}
                    breadcrumbs.insert(0, crumb_item)
                    last_crumb_tag_id = tag_id
            if parent_item_url is None:
                parent_item_url = host

            resize_css = None
            thumbnail_image_url = None
            full_image_url = None
            image_width = None
            image_height = None

            base_image_path = item.path
            if item.originalAlbumPath:
                base_image_path = item.originalAlbumPath

            if item.resizes:

                ordered_resizes = sorted(item.resizes, key=lambda r: r.width)

                css = utils.build_image_css(item, ordered_resizes)
                if css is None:
                    first = None
                    last = None
                    resize_css = None
                else:
                    first = css['first']
                    last = css['last']
                    resize_css = '<style>' + css['css'] + '</style>'

                if first is None:
                    resize_css = ''
                else:
                    thumbnail_image_url = utils.image_url(base_image_path, first)

                    full_image_url = utils.image_url(base_image_path, last)
                    image_width = last.width
                    image_height = last.height

            first_sibling = None
            previous_sibling = None
            next_sibling = None
            last_sibling = None

            if item.firstSibling is not None:
                first_sibling = {'title': item.firstSibling.title, 'url': item.firstSibling.path}

            if item.previousSibling is not None:
                previous_sibling = {'title': item.previousSibling.title, 'url': item.previousSibling.path}

            if item.nextSibling is not None:
                next_sibling = {'title': item.nextSibling.title, 'url': item.nextSibling.path}

            if item.lastSibling is not None:
                last_sibling = {'title': item.lastSibling.title, 'url': item.lastSibling.path}

            keywords_text = None
            if item.keywords:
                keywords_text = ",".join(item.keywords)

            show_share = utils.should_share(user_agent)

            views = 0
            if item.resizes:

                if tracking.is_sharing_callback(user_agent):
                    views = tracking.record_share(item.id, item.path)
                else:
                    if tracking.is_trackable(user_agent):
                        views = tracking.record_view(item.id, item.path)

            original_album_path = ''
            title = item.title
            if children is None:
                title = itemnaming.photo_title(item, 10000)

                if item.originalAlbumPath:
                    original_album_path = item.originalAlbumPath

            description = ''
            if item.description:
                md = markdown.Markdown()
                raw_description = item.description
                description = md.convert(raw_description)

            keywords = []
            if item.keywords:
                item_to_select = ''
                if item.path.startswith('/albums/'):
                    if item.breadcrumbs:
                        item_to_select = utils.path_to_tagId(item.breadcrumbs[-1].path) + '-' + utils.path_to_tagId(item.path)
                else:
                    item_to_select = utils.path_to_tagId(item.path)

                for keyword in item.keywords:
                    keyword_url = utils.generate_keyword_url(host, keyword, item_to_select)

                    keywords.append(
                        {'name': keyword, 'url': keyword_url}
                    )

            template_vals = {'host': host, 'path': search_path, 'track': track, 'hash': hash, 'users': users,
                             'title': title, 'item': item, 'children': children, 'breadcrumbs': breadcrumbs,
                             'resizecss': resize_css, 'staticurl': self.request.relative_url('/static'),
                             'thumbnail_url': thumbnail_image_url, 'fullImageUrl': full_image_url,
                             'fullImageWidth': image_width, 'fullImageHeight': image_height,
                             'firstSibling': first_sibling, 'previousSibling': previous_sibling,
                             'nextSibling': next_sibling, 'lastSibling': last_sibling,
                             'keywords': keywords, 'showShare': show_share, 'windowsShare': windows_share,
                             'parentItemUrl': parent_item_url, 'description': description,
                             'original_album_path': original_album_path, 'keywords': keywords,
                             'keywords_text': keywords_text}
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

        user_agent = self.request.headers.get('User-Agent', None)

        if utils.is_development() == False and self.request.scheme == 'http' and utils.device_supports_ssl_tni(user_agent):
            self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
            self.response.headers['Pragma'] = 'public'
            self.redirect(utils.redirect_url(self.request.path, self.request.query_string), permanent=True)

        search_path = self.request.path.lower()

        new_search_path = utils.convert_old_url(search_path)

        logging.info('Redirect to: ' + new_search_path)

        utils.add_response_headers(self.request, self.response.headers)
        self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
        self.response.headers['Pragma'] = 'public'
        self.redirect(utils.redirect_url(new_search_path, self.request.query_string), permanent=True)


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