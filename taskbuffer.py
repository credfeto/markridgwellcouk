
import webapp2
from google.appengine.api import mail
from google.appengine.api import urlfetch
import models
import utils

class TaskBufferHandler(webapp2.RequestHandler):

    def send_email(self, body, files, sender_address, subject, user_address):
        if files is None:
            mail.send_mail(sender=sender_address, to=user_address, subject=subject, body=body)
        else:
            mail.send_mail(sender=sender_address, to=user_address, subject=subject, body=body,
                           attachments=files)

    def strip_trailing_numbers(self, publish):
        return publish.title.rstrip('0123456789 ')

    def get_album_title(self, publish):

        album_title = None
        if publish.breadcrumbs is not None:
            album = publish.breadcrumbs[-1]
            if album is None:
                album_title = album.Title
                pos = album_title.find('-')
                if pos <> -1:
                    album_title = album_title[pos + 1:]
                album_title = album_title.strip()

        return album_title

    def contains_either(self, photo_title, album_title):
        if album_title in photo_title:
            return True

        if photo_title in album_title:
            return True

        return False

    def publish_photo(self, files, publish):
        # publish the item

        album_title = self.get_album_title(publish)
        title = self.strip_trailing_numbers(publish)
        if album_title is not None:
            if not self.contains_either(title.lower().trim(), album_title.lower().trim()):
                title = title + " - " + album_title
                if len(title) > 90:
                    title = title[:90]

        url = 'http://www.markridgwell.co.uk' + publish.path + '?utm_source=mtr&utm_medium=buffer&utm_campaign=publish'
        shortened_url = utils.shortern_url( url )
        self.response.out.write("Title: " + title + "\r\n")
        self.response.out.write("Short Url: " + shortened_url + "\r\n")
        user_address = 'buffer-62c71f8f12deed183390@to.bufferapp.com'
        sender_address = "Mark Ridgwell's Photos <bufferpublisher@markridgwellcouk.appspotmail.com>"
        subject = title + " #photo " + shortened_url
        body = "@profiles mark ridgwell's photos credfeto\r\n@link " + shortened_url
               ##"@now " \


        self.send_email(body, files, sender_address, subject, user_address)
        #self.send_email(body, files, sender_address, subject, 'markr@markridgwell.com')

    def get_resize(self, publish):
        ordered_resizes = sorted(publish.resizes, key=lambda r: r.width)
        image = ordered_resizes[-1]
        for (i, resize ) in enumerate(ordered_resizes):
            if resize.width <= 800:
                image = resize

        return image

    def fetch_image_to_attach(self, image, publish):
        image_url = utils.image_url(publish.path, image)
        self.response.out.write("Image: " + image_url + "\r\n")
        files = None
        result = urlfetch.fetch(image_url)
        self.response.out.write("Status: " + str(result.status_code) + "\r\n")
        if result.status_code == 200:
            filename = publish.title + ".jpg"
            file_data = result.content
            files = [(filename, file_data)]

            self.response.out.write("Adding Attachment: " + str(len(file_data)) + "bytes.\r\n")
        return files

    def get(self):

        utils.add_response_headers( self.request, self.response.headers )
        self.response.headers['Content-Type'] = "text/plain"

        items_to_publish = models.PublishableItem.query().fetch(1)
        if items_to_publish is not None:
            for itemToPublish in items_to_publish:
                
                self.response.out.write("Id: " + itemToPublish.id +"\r\n" )

                publish = models.GalleryItem.query(models.GalleryItem.id == itemToPublish.id ).get()
                if publish is not None:

                    image = self.get_resize(publish)

                    files = self.fetch_image_to_attach(image, publish)

                    self.publish_photo(files, publish)

                    #Remove the item we just published so it doesn't go again
                    itemToPublish.key.delete()
                    break

        self.response.out.write("OK")

app = webapp2.WSGIApplication([
    ('/tasks/buffer', TaskBufferHandler)
])