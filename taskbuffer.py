import urllib2

import webapp2
from google.appengine.api import mail
import models
import utils

class TaskBufferHandler(webapp2.RequestHandler):
    def get(self):

        utils.add_response_headers( self.request, self.response.headers )
        self.response.headers['Content-Type'] = "text/plain"

        items_to_publish = models.PublishableItem.query().fetch(1)
        if items_to_publish is not None:
            for itemToPublish in items_to_publish:
                
                self.response.out.write("Id: " + itemToPublish.id +"\r\n" )

                publish = models.GalleryItem.query(models.GalleryItem.id == itemToPublish.id ).get()
                if publish is not None:

                    ordered_resizes = sorted(publish.resizes, key=lambda r: r.width)
                    image = ordered_resizes[-1]
                    for (i, resize ) in enumerate(ordered_resizes):
                        if resize.width <= 800:
                            image = resize
                            break

                    imageUrl = utils.image_url(publish.path, image)

                    files = None
                    try:
                        result = urllib2.urlopen(imageUrl)
                        if result.status_code == 200:
                            filename = publish.title + ".jpg"
                            file_data = result.content
                            files = [filename, file_data]
                    except:
                        files = None

                    # publish the item
                    url = 'http://www.markridgwell.co.uk' + publish.path + '?utm_source=mtr&utm_medium=buffer&utm_campaign=publish'
                    shortenedUrl = url
                    user_address = 'buffer-62c71f8f12deed183390@to.bufferapp.com';                    
                    sender_address = "Mark Ridgwell's Photos <bufferpublisher@markridgwellcouk.appspotmail.com>"
                    subject = publish.title + " #photo " + shortenedUrl
                    body = "@profiles mark ridgwell's photos credfeto " \
                           "@now " \
                           "@url " + url

                    if files is None:
                        mail.send_mail(sender=sender_address, to=user_address, subject=subject, body=body)
                    else:
                        mail.send_mail(sender=sender_address, to=user_address, subject=subject, body=body,
                                       attachments=files)
                    
                    #Remove the item we just published so it doesn't go again
                    # itemToPublish.key.delete()
                    break

        self.response.out.write("OK")

app = webapp2.WSGIApplication([
    ('/tasks/buffer', TaskBufferHandler)
])
