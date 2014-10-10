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


class NotFoundHandler(webapp2.RequestHandler):
    def get(self):
        windowsshare = utils.enable_windows_share_metadata(self.request.headers.get('User-Agent', None))

        template_vals = {'host': self.request.host_url, 'path': searchPath, 'track': track, 'hash': hash,
                         'users': users, 'showShare': False, 'windowsshare': windowsshare}
        self.response.out.write(utils.render_template("notfound.html", template_vals))
        self.response.set_status(404)


app = webapp2.WSGIApplication([
    ('/.*', NotFoundHandler),
])