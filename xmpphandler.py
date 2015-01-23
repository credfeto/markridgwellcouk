import webapp2
from google.appengine.api import xmpp

import roster
import logging

class XMPPHandlerChat(webapp2.RequestHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)
        if message.body[0:5].lower() == 'hello':
            message.reply("Greetings!")

class XMPPHandlerSubscribe(webapp2.RequestHandler):
    def post(self):
        sender = self.request.get('from').split('/')[0]
        roster.add_contact(sender)

class XMPPHandlerSubscribed(webapp2.RequestHandler):
    def post(self):
        sender = self.request.get('from').split('/')[0]
        roster.add_contact(sender)

class XMPPHandlerUnsubscribe(webapp2.RequestHandler):
    def post(self):
        sender = self.request.get('from').split('/')[0]
        roster.remove_contact(sender)

class XMPPHandlerUnsubscribed(webapp2.RequestHandler):
    def post(self):
        sender = self.request.get('from').split('/')[0]
        roster.remove_contact(sender)

class XMPPHandlerError(webapp2.RequestHandler):
    def post(self):
        error_sender = self.request.get('from')
        error_stanza = self.request.get('stanza')
        logging.error('XMPP error received from %s (%s)', error_sender, error_stanza)

app = webapp2.WSGIApplication([
    ('/_ah/xmpp/message/chat/', XMPPHandlerChat),
    ('/_ah/xmpp/subscription/subscribe/', XMPPHandlerSubscribe),
    ('/_ah/xmpp/subscription/subscribed/', XMPPHandlerSubscribed),
    ('/_ah/xmpp/subscription/unsubscribe/', XMPPHandlerUnsubscribe),
    ('/_ah/xmpp/subscription/unsubscribed/', XMPPHandlerUnsubscribed),
    ('/_ah/xmpp/message/error/', XMPPHandlerError),
    ('/_ah/xmpp/error/', XMPPHandlerError),
])