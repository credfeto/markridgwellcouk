from google.appengine.api import mail
from google.appengine.api import urlfetch
import models
import utils
import itemnaming

from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
from google.appengine.api import mail

import models
import utils
import sys
from google.appengine.api import xmpp

def send_email(body, files, sender_address, subject, user_address):
    if files is None:
        mail.send_mail(sender=sender_address, to=user_address, subject=subject, body=body)
    else:
        mail.send_mail(sender=sender_address, to=user_address, subject=subject, body=body,
                       attachments=files)

def publish_photo(files, publish):
    # publish the item

    title_max_length = 90
    title = itemnaming.photo_title(publish, title_max_length)

    url = 'https://www.markridgwell.co.uk' + publish.path + '?utm_source=mtr&utm_medium=buffer&utm_campaign=publish'
    shortened_url = utils.shortern_url(url)

    #response.out.write("Title: " + title + "\r\n")
    #response.out.write("Short Url: " + shortened_url + "\r\n")

    user_address = 'buffer-62c71f8f12deed183390@to.bufferapp.com'
    sender_address = "Mark Ridgwell's Photos <bufferpublisher@markridgwellcouk.appspotmail.com>"
    subject = title + " #photo " + shortened_url
    body = "@profiles mark ridgwell's photos credfeto\r\n@link " + shortened_url
    # #"@now " \


    send_email(body, files, sender_address, subject, user_address)
    #send_email(body, files, sender_address, subject, 'markr@markridgwell.com')

    return utils.shortern_url('https://www.markridgwell.co.uk' + publish.path)

def get_resize(publish):
    ordered_resizes = sorted(publish.resizes, key=lambda r: r.width)
    image = ordered_resizes[-1]
    for (i, resize) in enumerate(ordered_resizes):
        if resize.width <= 800:
            image = resize

    return image

def fetch_image_to_attach(image, publish):
    image_url = utils.image_url(publish.path, image)
    #response.out.write("Image: " + image_url + "\r\n")
    files = None
    result = urlfetch.fetch(image_url)
    #response.out.write("Status: " + str(result.status_code) + "\r\n")
    if result.status_code == 200:
        filename = publish.title + ".jpg"
        file_data = result.content
        files = [(filename, file_data)]

        #response.out.write("Adding Attachment: " + str(len(file_data)) + "bytes.\r\n")
    return files

def delete_item_from_publish_queue(id):

        publish = models.PublishableItem.query(models.PublishableItem.id == id).get()
        if publish is not None:

            item = models.GalleryItem.query(models.GalleryItem.id == id).get()

            # Remove the item
            publish.key.delete()

            if item is not None:
                return 'Deleted: ' + item.path

            return 'Deleted: Unknown'

        else:
            return 'Item Not Found'

def publish_next():
    items_to_publish = models.PublishableItem.query().fetch(1)
    if items_to_publish is not None:
        for itemToPublish in items_to_publish:

            publish = models.GalleryItem.query(models.GalleryItem.id == itemToPublish.id).get()
            if publish is not None:
                image = get_resize(publish)

                files = fetch_image_to_attach(image, publish)
                if files is None:
                    msg = 'Could not retrieve image when publishing ' + publish.path + ' image : ' + utils.image_url(publish.path, image)
                    xmpp.send_message('markr@markridgwell.com', msg)

                url = publish_photo(files, publish)

                # Remove the item we just published so it doesn't go again
                itemToPublish.key.delete()
                return "Published: " + url

    return "Nothing published"