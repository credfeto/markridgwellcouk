import webapp2
from google.appengine.api import xmpp

import roster
import logging
import commonactions

class XMPPHandlerChat(webapp2.RequestHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)
        sender = self.request.get('from').split('/')[0]
        if sender == 'markr@markridgwell.com':
            if message.body[0:5].lower() == 'hello':
                message.reply("Greetings!")
            if message.body[0:10].lower() == 'unpublish:':
                message.reply(commonactions.delete_item_from_publish_queue(message.body[11:]))
            if message.body.lower().strip() == 'publish':
                message.reply(commonactions.publish_next())
        else:
            message.reply("huh?")

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

class XMPPHandlerPresenseAvailable(webapp2.RequestHandler):
    def post(self):
        # In the handler for _ah/xmpp/presence/available
        # Split the bare XMPP address (e.g., user@gmail.com)
        # from the resource (e.g., gmail.CD6EBC4A), and then send the
        # application's presence to the user.
        sender = self.request.get('from').split('/')[0]
        xmpp.send_presence(sender, status=self.request.get('status'), presence_show=self.request.get('show'))

class XMPPHandlerPresenseUnavailable(webapp2.RequestHandler):
    def post(self):
        # In the handler for _ah/xmpp/presence/available
        # Split the bare XMPP address (e.g., user@gmail.com)
        # from the resource (e.g., gmail.CD6EBC4A), and then send the
        # application's presence to the user.
        sender = self.request.get('from').split('/')[0]
        xmpp.send_presence(sender, status=self.request.get('status'), presence_show=self.request.get('show'))

class XMPPHandlerPresenseProbe(webapp2.RequestHandler):
    def post(self):
        # In the handler for _ah/xmpp/presence/available
        # Split the bare XMPP address (e.g., user@gmail.com)
        # from the resource (e.g., gmail.CD6EBC4A), and then send the
        # application's presence to the user.
        sender = self.request.get('from').split('/')[0]
        xmpp.send_presence(sender, status=self.request.get('status'), presence_show=self.request.get('show'))

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
    ('/_ah/xmpp/presence/available/', XMPPHandlerPresenseAvailable),
    ('/_ah/xmpp/presence/unavailable/', XMPPHandlerPresenseUnavailable),
    ('/_ah/xmpp/presence/probe/', XMPPHandlerPresenseProbe),
    ('/_ah/xmpp/message/error/', XMPPHandlerError),
    ('/_ah/xmpp/error/', XMPPHandlerError),
])