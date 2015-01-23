import webapp2

from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
from google.appengine.api import mail

import models
import utils
import sys
from google.appengine.api import xmpp


class TaskKillHandler(webapp2.RequestHandler):
    def get(self):

        utils.add_response_headers(self.request, self.response.headers)
        self.response.headers['Content-Type'] = "text/plain"

        id = 'cff7bc268029dbf1205927eba4a173aa03797cac03c48409f481be049a8803bef9dab95612cc406d719a25c1ab98fa285fc54199f491da127f5c17f26daa5ac2'

        status = ''

        publish = models.PublishableItem.query(models.PublishableItem.id == id).get()
        if publish <> None:


            # Remove the item
            publish.key.delete()

            status = 'Deleted'
            self.response.out.write("Deleted")
        else:
            status = 'Not Found'

        user_address = 'markr@markridgwell.com'
        #chat_message_sent = False
        msg = "Deletion status: " + status
        xmpp.send_invite(user_address)
        xmpp.send_message(user_address, msg)
        #status_code = xmpp.send_message(user_address, msg)
        #chat_message_sent = (status_code == xmpp.NO_ERROR)

        #if not chat_message_sent:

        self.response.out.write(status)


app = webapp2.WSGIApplication([
    ('/tasks/kill', TaskKillHandler)
])
