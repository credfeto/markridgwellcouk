import urllib
import urllib2
import utils
from google.appengine.api import urlfetch 
from google.appengine.api import taskqueue
from google.appengine.api import capabilities

def queue_update():

    if not utils.is_development():
        taskqueueEnabled = capabilities.CapabilitySet('taskqueue').is_enabled()
        if taskqueueEnabled:

            q = taskqueue.Queue('default')

            if not taskqueue.Task(name='publish'):
                q.add( url = 'tasks/publish', name = 'publish', countdown = 300 )

def update(hub, feed):

    data = {}
    data[ 'hub.mode' ] = 'publish';
    data[ 'hub.url' ] = feed;

    form_data = urllib.urlencode(data)

    result = urlfetch.fetch(url = hub,
                            payload = form_data,
                            method = urlfetch.POST,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'})