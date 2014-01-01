from google.appengine.ext.remote_api import remote_api_stub
import getpass
import sync

def auth_func():
  return (raw_input('Username:'), getpass.getpass('Password:'))

remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', auth_func,
                               'markridgwellcouk.appspot.com')

# sync.synchronize()