import webapp2
import utils
from google.appengine.api import xmpp
import commonactions


class TaskKillHandler(webapp2.RequestHandler):
    def get(self):

        utils.add_response_headers(self.request, self.response.headers)
        self.response.headers['Content-Type'] = "text/plain"

        id = 'cff7bc268029dbf1205927eba4a173aa03797cac03c48409f481be049a8803bef9dab95612cc406d719a25c1ab98fa285fc54199f491da127f5c17f26daa5ac2'

        status = commonactions.delete_item_from_publish_queue(id)

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
