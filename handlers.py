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

        if utils.is_development() == False and self.request.scheme == 'http' and utils.device_supports_ssl_tni(self.request.headers.get('User-Agent', None) ):
            self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
            self.response.headers['Pragma'] = 'public'
            self.redirect(utils.redirect_url(self.request.path, self.request.query_string), permanent=True)

        searchPath = self.request.path.lower()

        hash = utils.generate_url_hash(searchPath)

        q = models.GalleryItem.query(models.GalleryItem.id == hash)

        track = utils.should_track( self.request.headers )

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
                    self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
                    self.response.headers['Pragma'] = 'public'
                    self.redirect(utils.redirect_url(newSearchPath, self.request.query_string), permanent=True)
            
            if shouldReportError:
                template_vals = { 'path': searchPath, 'track': track, 'hash' : hash, 'users' : users, 'showShare': False }
                self.response.out.write(utils.render_template("notfound.html", template_vals))
                self.response.set_status(404) 
        else:
            children = None
            if item.children:
                children = []
                for child in item.children:
                    thumbnailUrl = None
                    if child.thumbnail:                        
                        thumbnailUrl = utils.image_url( 
                                                       child.path, child.thumbnail )

                    childItem = { 'id': child.id, 'path': child.path, 'title': child.title, 'type': child.type, 'description': child.description, 'thumbnail': child.thumbnail, 'thumbnailUrl' : thumbnailUrl }
                    children.append(childItem)

            resizecss = None;
            thumbnailImageUrl = None
            imageUrl = None
            imageWidth = None
            imageHeight = None
            if item.resizes:

                orderedResizes = sorted( item.resizes, key=lambda r: r.width )

                resizecss = '<style>'
                first = None
                last = None
                
                newLine = '' #'\n'
                imageMargin = 150
                for (i, resize ) in enumerate(orderedResizes):
                    if first is None:
                        first = resize #Set the default image size
                        resizecss = resizecss + newLine
                        resizecss = resizecss + '.image {' + newLine
                        resizecss = resizecss + '\twidth:' + str(resize.width) + 'px;' + newLine
                        resizecss = resizecss + '\theight:' + str(resize.height) + 'px;' + newLine
                        resizecss = resizecss + '\tmin-width:' + str(resize.width) + 'px;' + newLine
                        resizecss = resizecss + '\tmin-height:' + str(resize.height) + 'px;' + newLine
                        resizecss = resizecss + '\tmax-width:' + str(resize.width) + 'px;' + newLine
                        resizecss = resizecss + '\tmax-height:' + str(resize.height) + 'px;' + newLine                        
                        resizecss = resizecss + '\tbackground-image:url(\'' + utils.image_url( item.path, resize ) +'\');' + newLine
                        resizecss = resizecss + '}' + newLine
                        resizecss = resizecss + newLine

                    last = resize
                    resizecss = resizecss + newLine
                    if i < (len(item.resizes) - 1):
                            resizecss = resizecss + '@media (min-width: ' + str(resize.width + imageMargin) + 'px) and (max-width: ' + str(orderedResizes[i+1].width + imageMargin - 1) + 'px) {' + newLine
                    else:
                        resizecss = resizecss + '@media (min-width: ' + str(resize.width + imageMargin) + 'px) {' + newLine
                    resizecss = resizecss + '\t.image {' + newLine
                    resizecss = resizecss + '\t\twidth:' + str(resize.width) + 'px;' + newLine
                    resizecss = resizecss + '\t\theight:' + str(resize.height) + 'px;' + newLine
                    resizecss = resizecss + '\t\tmin-width:' + str(resize.width) + 'px;' + newLine
                    resizecss = resizecss + '\t\tmin-height:' + str(resize.height) + 'px;' + newLine
                    resizecss = resizecss + '\t\tmax-width:' + str(resize.width) + 'px;' + newLine
                    resizecss = resizecss + '\t\tmax-height:' + str(resize.height) + 'px;' + newLine                        
                    resizecss = resizecss + '\t\tbackground-image:url(\'' + utils.image_url( item.path, resize ) +'\');' + newLine
                    resizecss = resizecss + '\t}'
                    resizecss = resizecss + '}' + newLine
                    resizecss = resizecss + newLine

                    if i < (len(item.resizes) - 1):
                        retinaWidth = '(min-width: ' + str( (resize.width / 2 ) + imageMargin) + 'px) and (max-width: ' + str( ( orderedResizes[i+1].width / 2 ) + imageMargin - 1) + 'px)'

                        resizecss = resizecss + '@media only screen and (-Webkit-min-device-pixel-ratio: 1.5) and ' + retinaWidth + ', '
                        resizecss = resizecss + 'only screen and (-moz-min-device-pixel-ratio: 1.5) and ' + retinaWidth + ', '
                        resizecss = resizecss + 'only screen and (-o-min-device-pixel-ratio: 3/2) and ' + retinaWidth + ', '
                        resizecss = resizecss + 'only screen and (min-device-pixel-ratio: 1.5) and ' + retinaWidth + ' {' + newLine
                    else:
                        retinaWidth = '(min-width: ' + str( (resize.width / 2 ) + imageMargin) + 'px)'

                        resizecss = resizecss + '@media only screen and (-Webkit-min-device-pixel-ratio: 1.5) and ' + retinaWidth + ', '
                        resizecss = resizecss + 'only screen and (-moz-min-device-pixel-ratio: 1.5) and ' + retinaWidth + ', '
                        resizecss = resizecss + 'only screen and (-o-min-device-pixel-ratio: 3/2) and ' + retinaWidth + ', '
                        resizecss = resizecss + 'only screen and (min-device-pixel-ratio: 1.5) and ' + retinaWidth + ' {' + newLine

                    resizecss = resizecss + '\t.image {' + newLine
                    resizecss = resizecss + '\t\twidth:' + str(resize.width / 2) + 'px;' + newLine
                    resizecss = resizecss + '\t\theight:' + str(resize.height / 2) + 'px;' + newLine
                    resizecss = resizecss + '\t\tmin-width:' + str(resize.width / 2) + 'px;' + newLine
                    resizecss = resizecss + '\t\tmin-height:' + str(resize.height / 2) + 'px;' + newLine
                    resizecss = resizecss + '\t\tmax-width:' + str(resize.width / 2) + 'px;' + newLine
                    resizecss = resizecss + '\t\tmax-height:' + str(resize.height / 2) + 'px;' + newLine
                    resizecss = resizecss + '\t\tbackground-image:url(\'' + utils.image_url( item.path, resize ) +'\');' + newLine
                    resizecss = resizecss + '\t\tbackground-size:' + str(resize.width / 2) + 'px ' + str(resize.height / 2) + 'px;' + newLine
                    resizecss = resizecss + '\t}'
                    resizecss = resizecss + '}' + newLine
                    resizecss = resizecss + newLine

                resizecss = resizecss + '</style>'

                if first is None:
                    resizecss = ''
                else:
                    thumbnailImageUrl = utils.image_url( item.path, first )

                    imageUrl = utils.image_url( item.path, last )
                    imageWidth = last.width
                    imageHeight = last.height;


            firstSibling = None
            previousSibling = None
            nextSibling = None
            lastSibling = None

            if item.firstSibling <> None:
                firstSibling = { 'title' : item.firstSibling.title, 'url' : item.firstSibling.path }

            if item.previousSibling <> None:
                previousSibling = { 'title' : item.previousSibling.title, 'url' : item.previousSibling.path }

            if item.nextSibling <> None:
                nextSibling = { 'title' : item.nextSibling.title, 'url' : item.nextSibling.path }

            if item.lastSibling <> None:
                lastSibling = { 'title' : item.lastSibling.title, 'url' : item.lastSibling.path }

            keywords = None
            if item.keywords:
                keywords = ",".join(item.keywords)                

            showShare =  utils.should_share( self.request.headers.get( 'User-Agent', None ) )

            template_vals = { 'path': searchPath, 'track': track, 'hash' : hash, 'users' : users, 'title' : item.title, 'item' : item, 'children' : children, 'resizecss' : resizecss, 'staticurl' : self.request.relative_url('/static'), 'thumbnailUrl' : thumbnailImageUrl, 'fullImageUrl' : imageUrl, 'fullImageWidth' : imageWidth, 'fullImageHeight' : imageHeight, 'firstSibling' : firstSibling, 'previousSibling' : previousSibling, 'nextSibling' : nextSibling, 'lastSibling' : lastSibling, 'keywords' : keywords, 'showShare' : showShare }
            self.response.out.write(utils.render_template("index.html", template_vals))
            self.response.headers['Strict-Transport-Security'] = 'max-age=31536000'
            self.response.headers['P3P'] = 'max-age=31536000'
            self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
            self.response.headers['Pragma'] = 'public'

app = webapp2.WSGIApplication([
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