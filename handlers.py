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


class IndexHandler(webapp2.RequestHandler):
    def get(self):

        searchPath = self.request.path.lower()

        hash = utils.generate_url_hash(searchPath)

        q = models.GalleryItem.query(models.GalleryItem.id == hash)

        item = q.get()
        if item is None:
            template_vals = { 'path': searchPath, 'hash' : hash, 'users' : users }
            self.response.out.write(utils.render_template("notfound.html", template_vals))
            self.response.set_status(404) 
        else:
            children = None
            if item.children:
                children = []
                for child in item.children:
                    thumbnailUrl = None
                    if child.thumbnail:                        
                        thumbnailUrl = utils.image_url( child.path, child.thumbnail )

                    childItem = { 'id': child.id, 'path': child.path, 'title': child.title, 'type': child.type, 'description': child.description, 'thumbnail': child.thumbnail, 'thumbnailUrl' : thumbnailUrl }
                    children.append(childItem)

            resizecss = None;
            if item.resizes:

                orderedResizes = sorted( item.resizes, key=lambda r: r.width )

                resizecss = '<style>'
                first = None
                
                for (i, resize ) in enumerate(orderedResizes):
                    if first is None:
                        first = resize #Set the defauult image size
                        resizecss = resizecss + '\n'
                        resizecss = resizecss + '\t.image {\n'
                        resizecss = resizecss + '\twidth:' + str(resize.width) + 'px;\n'
                        resizecss = resizecss + '\theight:' + str(resize.height) + 'px;\n'
                        resizecss = resizecss + '\tmin-width:' + str(resize.width) + 'px;\n'
                        resizecss = resizecss + '\tmin-height:' + str(resize.height) + 'px;\n'
                        resizecss = resizecss + '\tmax-width:' + str(resize.width) + 'px;\n'
                        resizecss = resizecss + '\tmax-height:' + str(resize.height) + 'px;\n'                        
                        resizecss = resizecss + '\tbackground-image:url(\'' + utils.image_url( item.path, resize ) +'\');\n'
                        resizecss = resizecss + '}\n'
                        resizecss = resizecss + '\n'

                    resizecss = resizecss + '\n'
                    if i < (len(item.resizes) - 1):
                            resizecss = resizecss + '@media (min-width: ' + str(resize.width + 20) + 'px) and (max-width: ' + str(orderedResizes[i+1].width + 19) + 'px) {\n'
                    else:
                        resizecss = resizecss + '@media (min-width: ' + str(resize.width) + 'px) {\n'
                    resizecss = resizecss + '\t.image {\n'
                    resizecss = resizecss + '\t\twidth:' + str(resize.width) + 'px;\n'
                    resizecss = resizecss + '\t\theight:' + str(resize.height) + 'px;\n'
                    resizecss = resizecss + '\t\tmin-width:' + str(resize.width) + 'px;\n'
                    resizecss = resizecss + '\t\tmin-height:' + str(resize.height) + 'px;\n'
                    resizecss = resizecss + '\t\tmax-width:' + str(resize.width) + 'px;\n'
                    resizecss = resizecss + '\t\tmax-height:' + str(resize.height) + 'px;\n'                        
                    resizecss = resizecss + '\t\tbackground-image:url(\'' + utils.image_url( item.path, resize ) +'\');\n'
                    resizecss = resizecss + '\t}'
                    resizecss = resizecss + '}\n'
                    resizecss = resizecss + '\n'
                if first is None:
                    resizecss = resizecss + 'wtf'
                resizecss = resizecss + '</style>'

            template_vals = { 'path': searchPath, 'hash' : hash, 'users' : users, 'title' : item.title, 'item' : item, 'children' : children, 'resizecss' : resizecss }
            self.response.out.write(utils.render_template("index.html", template_vals))


class ResizeImageHandler(webapp2.RequestHandler):
    def get(self):

        pos = self.request.path.rfind('/') + 1
        searchPath = self.request.path.lower()[ 6 : pos ]
        width = self.request.path[ pos : -10 ]

        hash = utils.generate_url_hash(searchPath)

        template_vals = { 'path': searchPath + ':' + width, 'hash' : hash, 'users' : users }
        self.response.out.write(utils.render_template("index.html", template_vals))

class ThumbnailImageHandler(webapp2.RequestHandler):
    def get(self):
        searchPath = self.request.path.lower()[ 10 : -13 ]

        hash = utils.generate_url_hash(searchPath)

        template_vals = { 'path': searchPath, 'hash' : hash, 'users' : users }
        self.response.out.write(utils.render_template("index.html", template_vals))

app = webapp2.WSGIApplication([
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/thumbnail/[\w\-]*/thumbnail\.jpg', ThumbnailImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
    ('/image/[\w\-]*/[0-9]+_image\.jpg', ResizeImageHandler),
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
])