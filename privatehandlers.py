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
import handlers

class PrivateIndexHandler(handlers.IndexHandler):
    def get(self):

        now = datetime.datetime.now()

        user = users.get_current_user()        
        if user:
            q = db.GqlQuery("SELECT * FROM UserPrefs WHERE userid = :1", user.user_id())
            userprefs = q.get()

            if userprefs:
                if userprefs.banned:
                    self.response.set_status(403) 
                    return
                
                delta = now - userprefs.lastAccessed

                if delta > datetime.timedelta( hours = 1):
                    userprefs.lastAccesed = now
                    userprefs.put()

            else:
                userprefs = models.UserPrefs(
                                             userid = user.user_id(),
                                             lastEmailAddress = user.email(),
                                             lastNickname = user.nickname(),
                                             banned = False,
                                             firstLoggedIn = now,
                                             lastAccessed = now
                                             )
                userprefs.put()

        return handlers.IndexHandler.get(self)

app = webapp2.WSGIApplication([
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/[\w\-]*/thumbnail\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/thumbnail/[\w\-]*/[\w\-]*/thumbnail\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/thumbnail/[\w\-]*/thumbnail\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/image/[\w\-]*/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/image/[\w\-]*/[\w\-]*/[0-9]+_image\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/image/[\w\-]*/[0-9]+_image\.jpg', handlers.LegacyUrlNotFoundNotFoundHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/', PrivateIndexHandler),
    ('/[\w\-]*/', PrivateIndexHandler),    
    ('/', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/~[0-9]+', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/~[0-9]+', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/~[0-9]+', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/~[0-9]+', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/~[0-9]+', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/~[0-9]+', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/~[0-9]+', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/~[0-9]+', PrivateIndexHandler),
    ('/[\w\-]*/~[0-9]+', PrivateIndexHandler),    
    ('/~[0-9]+', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*/[\w\-]*', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*/[\w\-]*', PrivateIndexHandler),
    ('/[\w\-]*/[\w\-]*', PrivateIndexHandler),
    ('/[\w\-]*', PrivateIndexHandler),    
])