import urllib
import urllib2
from google.appengine.api import urlfetch 
from google.appengine.api import taskqueue

def queue_update():

    taskqueueEnabled = capabilities.CapabilitySet('taskqueue').is_enabled()
    if taskqueueEnabled:

        q = taskqueue.Queue('default')

        if not taskqueue.Task(name='publish'):
            q.add(url='tasks/publish', name='publish')

def update(hub, feed):

    data = {}
    data[ 'hub.mode' ] = 'publish';
    data[ 'hub.url' ] = feed;

    form_data = urllib.urlencode(data)

    result = urlfetch.fetch(url = hub,
                            payload = form_data,
                            method = urlfetch.POST,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'})