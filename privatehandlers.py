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

                if delta > datetime.timedelta(hours=1):
                    userprefs.lastAccesed = now
                    userprefs.put()

            else:
                userprefs = models.UserPrefs(
                    userid=user.user_id(),
                    lastEmailAddress=user.email(),
                    lastNickname=user.nickname(),
                    banned=False,
                    firstLoggedIn=now,
                    lastAccessed=now
                )
                userprefs.put()

                sender_address = "Mark Ridgwell's Photos <newusernotification@markridgwellcouk.appspotmail.com>"
                host = self.request.host_url
                mail.send_mail_to_admins(sender_address, "New user logged in",
                                         "User " + userprefs.lastEmailAddress + " logged in to " + host)

        return handlers.IndexHandler.get(self)


app = webapp2.WSGIApplication([
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